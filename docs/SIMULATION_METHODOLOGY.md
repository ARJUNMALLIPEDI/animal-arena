# Simulation Methodology

This document explains exactly how Animal Arena decides a matchup. The goal is
that every number the UI shows can be traced back to a documented rule here —
nothing is an LLM guess, and nothing is a hidden magic constant.

The whole engine lives in `backend/app/simulation/` and has **zero
dependencies on FastAPI, SQLAlchemy, or any LLM**. It is a plain Python/NumPy
library you can import and unit test on its own (see
`backend/tests/test_simulation_engine.py`).

## 1. Animal data model

Every animal has two tiers of data (`backend/app/data/seed/build_seed_data.py`):

**Measured fields** — average/max weight, length, top speed, and bite force
(where meaningfully documented) — are drawn from commonly cited public
biological reference ranges. These are real numbers, not invented, though
species-level averages naturally vary by source.

**Combat attributes** (0–100 scale): `size`, `strength`, `speed`, `agility`,
`defense`, `weapon`, `endurance`. Two of these are *derived*:

- `size` — a log-scale, min-max normalization of average weight across the
  whole roster (log scale because weight spans three orders of magnitude,
  from a 1.2 kg fennec fox to a 5,000 kg elephant).
- `speed` — a min-max normalization of top speed across the roster.

The other five (`strength`, `agility`, `defense`, `weapon`, `endurance`) have
no standardized cross-species scientific measurement, so they are the
project's own **informed combat-relevance ratings**, assigned per animal from
its documented physical capabilities and behavior (e.g. a Nile crocodile's
`weapon` score reflects having the strongest documented bite force of any
living animal; a cheetah's `endurance` score reflects that it can only
sustain a sprint for seconds). Every animal record carries an
`attribute_sources` map tagging each attribute `"derived"` or `"estimated"`,
and the UI surfaces this distinction rather than presenting estimates as fact.

## 2. Environment modifiers

Each environment (`backend/app/simulation/environment.py`) carries a small
rule table. A rule grants a bonus to specific attributes when the animal has
a matching adaptation or habitat tag (e.g. `cold_resistant` in Arctic → +12%
`endurance` and `defense`), and a penalty when the animal is a poor fit (e.g.
a purely `aquatic` animal outside the Ocean environment, or an animal with an
explicitly mismatched tag such as `desert_adapted` in the Arctic).

**The cap that keeps this sane:** every modifier is applied as a multiplier,
and `CombatAttributes.scaled()` hard-clamps the *net* change for any single
attribute to **±15%**, regardless of how many rules stack. This was an
explicit design requirement — environment should nudge a matchup, not
invalidate it. The full rule table is in `environment.py` and is short enough
to read end to end; nothing is tuned by trial and error to produce a
"balanced" outcome.

## 3. Combat Effectiveness Score (CES)

A single weighted sum used only for the post-hoc "key factors" explanation
and as a sanity check — **not** what decides the winner:

```
CES = 0.14·size + 0.20·strength + 0.10·speed + 0.11·agility
    + 0.15·defense + 0.20·weapon + 0.10·endurance
```

Weights are centralized in `backend/app/simulation/weights.py` and sum to 1.0.

## 4. The actual simulation: per-round Monte Carlo combat

Comparing two CES numbers would be a formula, not a simulation, and it would
produce no distribution, no round count, and no sense of "the underdog
occasionally wins." Instead, `run_simulation()` in `engine.py` simulates each
individual encounter as a sequence of rounds, run **for every encounter in
the batch simultaneously** as vectorized NumPy arrays (not a Python loop per
encounter — a loop over rounds, each iteration processing all N encounters at
once):

1. **Health pools.** Each animal starts with `health = 55 + 0.65·(0.45·size + 0.55·endurance)`,
   so bigger, tougher animals can absorb more damage before going down.

2. **Per-encounter "form."** Once per simulated encounter (not per round), a
   Gaussian multiplier (`σ = 0.16`) is drawn per animal and applied to both
   its offense and defense for that entire encounter. This represents
   day-to-day variability — a bit of luck, terrain angle, alertness — and is
   what keeps a real statistical edge from collapsing into a near-certain
   100%-0% outcome once compounded over several rounds (per-round noise alone
   averages out across a multi-round encounter, which is standard random-walk
   behavior; this was confirmed empirically while tuning the engine, see the
   git history of `tests/test_simulation_engine.py`).

3. **Each round**, both animals attack simultaneously:
   - `offense = 0.5·strength + 0.5·weapon` (± per-round Gaussian noise, σ=9)
   - `guard = 0.5·defense + 0.3·agility + 0.2·speed` (± noise, σ=5.4)
   - `damage = max(0, offense − guard) × 0.55 × (1 − 0.0018·endurance)` — the
     endurance term is a small "grit" discount on incoming damage.
   - Both health pools are reduced simultaneously; the round is scored even
     if one animal would already be at zero, so a mutual knockout (draw) is
     possible.

4. **Resolution.** The loop continues until one health pool reaches zero, or
   a 40-round cap is hit, at which point the higher remaining health % wins
   (a tie at the cap, or both animals reaching zero the same round, is
   recorded as a draw).

5. **What-if overrides** (equalizing an attribute, or setting one directly)
   are applied to each animal's *environment-adjusted* attributes before the
   round loop runs, so "what if they weighed the same" and "what if this
   happened in the Arctic" compose correctly.

## 5. Aggregation

Across `num_simulations` runs (default 10,000, bounded 100–50,000):

- **Win/loss/draw counts and percentages.**
- **Average and standard deviation of rounds-to-resolution** — this is the
  "average encounter duration" the spec asks for, and it only exists because
  combat is modeled round by round rather than as one formula.
- **Key factors** — the top 3 attributes by `|weight × (attr_a − attr_b)|`,
  i.e. which attribute gaps contributed most to the CES difference. This is
  what the AI commentary layer is allowed to reference (see below).

## 6. Determinism

`run_simulation(..., seed=42)` is fully reproducible: the same two animals,
environment, and seed always produce the same aggregate result. This is what
makes the engine unit-testable (`TestDeterminism` in the test suite) and is
exposed in the API so a user can reproduce a specific interesting result.

## 7. What the AI commentary layer does and does not do

The `/api/commentary` endpoint sends the **already-computed** result (win
percentages, round stats, effective attributes, key factors) to the LLM as
structured JSON, with an explicit system prompt instruction that the model
must not invent numbers, must not decide or influence the winner, and must
not claim scientific validity. If no API key is configured, or the LLM call
fails for any reason, a deterministic template built directly from the
simulation data is used instead — the app never blocks on, or silently
depends on, the LLM being available. See
`backend/app/services/commentary_service.py`.

## 8. Known limitations

- Combat attributes for `strength`, `agility`, `defense`, `weapon`, and
  `endurance` are the project's own estimates, not peer-reviewed
  measurements — real animal combat has never been systematically studied or
  measured this way, for good reason. This is disclosed throughout the UI.
- The combat model does not account for pack/group dynamics beyond a
  `fighting_style` label, individual health/age/condition, or terrain within
  an environment (e.g. a specific river bank vs. open savanna).
- Environment modifiers are a deliberately simple, capped, linear system —
  not a claim about the exact magnitude of any real environmental advantage.
