"""
AI commentary layer.

Design constraint (per project spec): the LLM never decides a winner and
never invents statistics. It receives the *already-computed* simulation
result as structured JSON and is instructed, explicitly and repeatedly in
the prompt, to explain that data rather than generate new numbers. This
module is the only place in the codebase that talks to an LLM API.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.animal import Animal
from app.models.commentary import Commentary
from app.models.matchup import Matchup
from app.schemas.commentary import CommentaryOut, CommentaryStyle

logger = logging.getLogger(__name__)

STYLE_INSTRUCTIONS: dict[str, str] = {
    "scientific": (
        "Write in a precise, neutral, scientific tone, as if summarizing a "
        "model's output for a research audience. Reference specific attribute "
        "differentials and mechanisms (mass, bite force, defense, etc.)."
    ),
    "sports": (
        "Write like an energetic sports commentator recapping a match. Be "
        "vivid and engaging, but every claim must still trace back to the "
        "provided simulation numbers -- no invented plays or moments."
    ),
    "documentary": (
        "Write like a calm nature-documentary narrator (in the style of a "
        "wildlife documentary voiceover), explaining the outcome in terms of "
        "each animal's natural adaptations and behavior."
    ),
}

SYSTEM_PROMPT = """You are the commentary layer for Animal Arena, a hypothetical \
entertainment simulation of animal matchups.

You will be given the complete, final output of a deterministic/statistical combat \
simulation: win percentages, round counts, effective attribute values (already \
adjusted for environment), and the top statistical "key factors" the simulation \
identified.

Rules you must follow exactly:
1. You do NOT decide or influence the winner. The winner is already decided by the \
   simulation data you are given -- your only job is to explain it.
2. You must NOT invent, estimate, or restate any number that is not present in the \
   provided data. Every statistic you mention (percentages, attribute values, round \
   counts) must come directly from the JSON you are given.
3. You must NOT claim this is a scientifically validated prediction of real combat. \
   Treat it explicitly as a hypothetical, probabilistic entertainment model.
4. Keep the response to 3-5 sentences.
5. You may describe qualitative animal behavior/biology (e.g. "grizzly bears rely on \
   raw power") as general context, but any quantitative claim must be grounded in the \
   provided data.
"""


def _build_user_prompt(
    animal_a: Animal, animal_b: Animal, matchup: Matchup, style: CommentaryStyle
) -> str:
    import json

    data = {
        "animal_a": animal_a.common_name,
        "animal_b": animal_b.common_name,
        "environment_id": matchup.environment_id,
        "num_simulations": matchup.num_simulations,
        "animal_a_win_pct": round(matchup.win_pct_a, 1),
        "animal_b_win_pct": round(matchup.win_pct_b, 1),
        "draws": matchup.draws,
        "avg_encounter_rounds": round(matchup.avg_rounds, 1),
        "std_encounter_rounds": round(matchup.std_rounds, 1),
        "combat_effectiveness_score_a": round(matchup.ces_a, 1),
        "combat_effectiveness_score_b": round(matchup.ces_b, 1),
        "effective_attributes_a": matchup.effective_attributes_a,
        "effective_attributes_b": matchup.effective_attributes_b,
        "key_factors": matchup.key_factors,
        "what_if_overrides_applied": matchup.what_if_overrides,
    }
    style_instruction = STYLE_INSTRUCTIONS[style]
    return (
        f"Style: {style}. {style_instruction}\n\n"
        f"Simulation result (the ONLY source of numbers you may use):\n"
        f"{json.dumps(data, indent=2)}\n\n"
        f"Write the commentary now."
    )


def _fallback_commentary(animal_a: Animal, animal_b: Animal, matchup: Matchup) -> str:
    """Deterministic, data-only fallback used when no API key is configured
    or the LLM call fails -- the app should never be blocked on the LLM."""
    winner = animal_a.common_name if matchup.win_pct_a >= matchup.win_pct_b else animal_b.common_name
    win_pct = max(matchup.win_pct_a, matchup.win_pct_b)
    top_factor = matchup.key_factors[0] if matchup.key_factors else None
    factor_text = f" driven mainly by a {top_factor['attribute']} advantage" if top_factor else ""
    return (
        f"Across {matchup.num_simulations:,} simulated encounters, {winner} won "
        f"{win_pct:.1f}% of the time{factor_text}. Average encounters lasted "
        f"{matchup.avg_rounds:.1f} rounds. This is a hypothetical, probabilistic "
        f"model, not a scientifically validated prediction."
    )


def generate_commentary(db: Session, matchup_id: str, style: CommentaryStyle, force_refresh: bool = False) -> CommentaryOut:
    matchup = db.get(Matchup, matchup_id)
    if matchup is None:
        raise ValueError(f"matchup '{matchup_id}' not found")

    if not force_refresh:
        cached = (
            db.query(Commentary)
            .filter(Commentary.matchup_id == matchup_id, Commentary.style == style)
            .order_by(Commentary.created_at.desc())
            .first()
        )
        if cached is not None:
            return CommentaryOut(matchup_id=matchup_id, style=style, text=cached.text, created_at=cached.created_at)

    animal_a = db.get(Animal, matchup.animal_a_id)
    animal_b = db.get(Animal, matchup.animal_b_id)

    settings = get_settings()
    text: str
    generated_by_llm = True

    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY not set; using deterministic fallback commentary")
        text = _fallback_commentary(animal_a, animal_b, matchup)
        generated_by_llm = False
    else:
        try:
            text = _call_anthropic(settings, animal_a, animal_b, matchup, style)
        except Exception:
            logger.exception("LLM commentary call failed; falling back to deterministic summary")
            text = _fallback_commentary(animal_a, animal_b, matchup)
            generated_by_llm = False

    record = Commentary(matchup_id=matchup_id, style=style, text=text)
    db.add(record)
    db.commit()
    db.refresh(record)

    return CommentaryOut(
        matchup_id=matchup_id, style=style, text=text, created_at=record.created_at, generated_by_llm=generated_by_llm
    )


def _call_anthropic(settings, animal_a: Animal, animal_b: Animal, matchup: Matchup, style: CommentaryStyle) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(animal_a, animal_b, matchup, style)}],
    )
    return "".join(block.text for block in message.content if hasattr(block, "text")).strip()
