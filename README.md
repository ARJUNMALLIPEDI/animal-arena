# Animal Arena

**Who would actually win?** Animal Arena is a full-stack, hypothetical animal
matchup simulator. Pick two animals and an environment, and a deterministic/
probabilistic combat engine runs thousands of independent, randomized
encounters and reports a statistical result — win percentages, average
encounter length, and the attribute gaps that mattered most. An LLM is used
**only** to narrate that result afterward, in a choice of styles; it never
decides the outcome and is instructed not to invent numbers.

> **This is entertainment, not science.** Animal Arena is a hypothetical
> simulation built on a designed, partly-estimated scoring model — not a
> scientifically validated prediction of how real animals would fight. The
> UI says this on every page; this README says it too.

## Table of contents

- [What it does](#what-it-does)
- [Architecture](#architecture)
- [Simulation methodology](#simulation-methodology)
- [Tech stack](#tech-stack)
- [Running it locally](#running-it-locally)
- [API reference](#api-reference)
- [Example matchup](#example-matchup)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Limitations](#limitations)
- [Future improvements](#future-improvements)

## What it does

- **Matchup simulator** — pick any two of 47 animals, choose one of 7
  environments, and run 100–50,000 simulated encounters. Get a win
  percentage for each animal, an average encounter length, and the specific
  attribute differences the simulation identified as decisive.
- **Stylized battle animation** — a non-graphic, arena-style animation
  (icons enter, clash, settle on a result) built with Framer Motion.
- **Animal database** — 47 animals with real measured biological data
  (weight, length, top speed, bite force where documented) alongside a
  clearly labeled, documented combat-attribute model.
- **Tournament mode** — pick 4, 8, or 16 animals and generate a single-
  elimination bracket, resolved with the same simulation engine, visualized
  as a bracket with a crowned champion.
- **What-if mode** — equalize any attribute between the two animals (e.g.
  "what if they weighed the same"), or override an attribute directly (e.g.
  "what if the tiger had the lion's strength"), and re-run the simulation.
- **AI commentary** — after a simulation finishes, get it explained in a
  scientific, sports-commentator, or nature-documentary voice, generated
  from the simulation's actual numbers.
- **Statistics dashboard** — aggregate win rates and matchup history across
  every simulation run this session.

## Architecture

Full write-up (with diagram) in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
The short version:

```
React/TS frontend  <-- REST/JSON -->  FastAPI backend
                                          |
                                          +-- simulation/ engine (pure Python + NumPy,
                                          |     zero framework dependencies, unit tested alone)
                                          +-- SQLAlchemy models -> SQLite (dev) / PostgreSQL (prod)
                                          +-- Anthropic API (commentary only, server-side key)
```

The simulation engine has no dependency on the web framework, the database,
or the LLM — it's a standalone library that takes structured animal +
environment data in and returns statistical results out. This is what makes
"the outcome isn't an LLM guess" a verifiable property rather than a claim:
you can run `pytest backend/tests/test_simulation_engine.py` with the
backend server, database, and API key all absent.

## Simulation methodology

Full write-up in
[`docs/SIMULATION_METHODOLOGY.md`](docs/SIMULATION_METHODOLOGY.md). Summary:

1. Each animal has 7 normalized (0–100) combat attributes. Two (`size`,
   `speed`) are derived from real measured data via a documented
   normalization; the other five are the project's own labeled, documented
   estimates (there is no standardized scientific measurement of "animal
   strength" or "animal agility" across species).
2. The chosen environment applies capped (±15% max, per attribute) modifiers
   based on each animal's adaptations/habitat tags.
3. Each individual encounter is simulated round by round — not as one
   formula — with per-round randomness and a per-encounter "form" factor,
   until one animal's health pool is depleted or a round cap is hit.
4. This is repeated for the full batch (default 10,000, vectorized with
   NumPy) to produce win percentages, round-count statistics, and the
   attribute gaps that contributed most to the result.
5. Everything is seedable and fully reproducible.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion, Recharts, React Query, Zustand, React Router |
| Backend | Python, FastAPI, Pydantic v2 |
| Simulation | Pure Python + NumPy (vectorized Monte Carlo) |
| Database | SQLite (dev) via SQLAlchemy 2.0, swappable to PostgreSQL with zero code changes |
| LLM | Anthropic API (`anthropic` SDK), server-side only |
| Testing | pytest (unit + API), TypeScript build check |

## Running it locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) an Anthropic API key, for real AI commentary — the app works
  fully without one, using a deterministic data-only commentary fallback.

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # edit .env if you want to set ANTHROPIC_API_KEY

uvicorn app.main:app --reload --port 8000
```

The database (SQLite by default) is created and seeded with all 47 animals
and 7 environments automatically on first startup. API docs are then at
`http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local        # defaults to http://localhost:8000, edit if needed
npm run dev
```

Open `http://localhost:5173`.

### Running both together

Two terminals — one running the backend on port 8000, one running the
frontend on port 5173 (Vite's dev server proxies nothing; the frontend talks
to the backend directly via `VITE_API_BASE_URL`, and the backend's CORS
config allows `http://localhost:5173` by default).

## API reference

Interactive OpenAPI docs are auto-generated at `/docs` once the backend is
running. Key endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/animals` | List animals (filter by `category`, `habitat`, `search`) |
| GET | `/api/animals/{id}` | Single animal profile |
| GET | `/api/environments` | List environments |
| POST | `/api/matchups/simulate` | Run a simulation, get the full result |
| GET | `/api/matchups` | Matchup history |
| GET | `/api/matchups/{id}` | A single stored matchup |
| POST | `/api/tournaments` | Create a bracket (4/8/16/32 animals) |
| GET | `/api/tournaments/{id}` | Bracket state |
| POST | `/api/tournaments/{id}/advance` | Simulate the next round(s) |
| POST | `/api/commentary` | Generate/fetch AI commentary for a matchup |
| GET | `/api/stats/dashboard` | Aggregate stats across all matchups |

### Example request

```bash
curl -X POST http://localhost:8000/api/matchups/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "animal_a_id": "african_lion",
    "animal_b_id": "grizzly_bear",
    "environment_id": "open_plains",
    "num_simulations": 10000,
    "seed": 42
  }'
```

### What-if example

```bash
curl -X POST http://localhost:8000/api/matchups/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "animal_a_id": "siberian_tiger",
    "animal_b_id": "grizzly_bear",
    "environment_id": "arctic",
    "equalize_attributes": ["size"]
  }'
```

## Example matchup

African Lion vs. Grizzly Bear, Open Plains, 10,000 simulations, seed 42
(actual output from this codebase):

```
Grizzly Bear: 61.8%   (6,176 wins)
African Lion: 36.4%   (3,638 wins)
Draws:         1.9%   (186)

Average encounter length: 7.66 ± 2.55 rounds

Key factors:
  Defense  — Grizzly Bear favored (+23.0 pts)
  Speed    — African Lion favored (+28.5 pts)
  Strength — Grizzly Bear favored (+14.0 pts)
```

This is in the same range as the example in the original spec (Grizzly
~67%/Lion ~33%) — close but not identical, because it comes from an actual
Monte Carlo run against this project's specific attribute values, not a
hand-picked number.

## Testing

```bash
cd backend
source venv/bin/activate
pytest                     # 40 tests: simulation engine unit tests + full API test suite
```

```bash
cd frontend
npx tsc -b                 # type check
npm run build               # production build
```

The simulation engine tests (`tests/test_simulation_engine.py`) exercise the
engine directly with no server, database, or API key — determinism,
symmetry between identical animals, environment modifier caps, and the
what-if override logic. The API tests
(`tests/test_api_*.py`) spin up the FastAPI app against an isolated
throwaway SQLite database via `TestClient` and cover every endpoint,
including validation and 404 error paths.

## Project structure

```
animal-arena/
├── backend/
│   ├── app/
│   │   ├── simulation/      # pure engine: attributes, environment modifiers, Monte Carlo core
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── routers/         # FastAPI endpoints
│   │   ├── services/        # business logic: matchup, tournament, commentary, DB<->engine mapping
│   │   ├── data/seed/       # animal + environment seed data + generation/loading scripts
│   │   └── main.py
│   └── tests/                # unit tests (engine) + API tests (FastAPI TestClient)
├── frontend/
│   └── src/
│       ├── api/               # typed API client functions
│       ├── types/             # TypeScript types mirroring backend schemas
│       ├── store/             # Zustand UI state
│       ├── hooks/             # React Query hooks
│       ├── components/        # animals/, battle/, charts/, tournament/, commentary/, common/
│       └── pages/              # Home, AnimalDatabase, TournamentPage, Dashboard
└── docs/
    ├── ARCHITECTURE.md
    └── SIMULATION_METHODOLOGY.md
```

## Limitations

- The five estimated combat attributes (strength, agility, defense, weapon,
  endurance) are this project's own informed ratings, not peer-reviewed
  measurements — no such standardized cross-species dataset exists.
- The model doesn't account for individual animal condition/age, pack
  hunting dynamics beyond a `fighting_style` label, or specific terrain
  features within an environment.
- 47 animals are seeded; adding more is a matter of extending
  `backend/app/data/seed/build_seed_data.py`.
- No authentication/accounts — matchup and tournament history is stored but
  anonymous.
- No production deployment configuration is included; this targets a clean
  local run.

## Future improvements

- Expand the roster past 47 animals and add real photography/illustration.
- Per-animal condition modifiers (injury, hunger) as an additional what-if axis.
- User accounts and saved/shareable matchup and tournament links.
- A second simulation "mode" that models pack/group encounters explicitly
  rather than 1v1 only.
- Postgres + Alembic migration setup for production deployment.
- Code-splitting the frontend bundle (currently a single ~900 KB chunk).
