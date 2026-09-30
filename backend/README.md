# Animal Arena — Backend

FastAPI backend and simulation engine for Animal Arena.

See the [project root README](../README.md) for the full write-up and
[docs/SIMULATION_METHODOLOGY.md](../docs/SIMULATION_METHODOLOGY.md) for how
the combat engine works.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The database is created and seeded automatically on first startup. API docs:
`http://localhost:8000/docs`.

## Tests

```bash
pytest                  # all tests
pytest tests/test_simulation_engine.py   # engine only, no server/DB needed
pytest --cov=app         # with coverage
```

## Layout

- `app/simulation/` — the pure combat engine (no framework dependencies)
- `app/models/` — SQLAlchemy models
- `app/schemas/` — Pydantic request/response models
- `app/routers/` — FastAPI endpoints
- `app/services/` — business logic (matchup, tournament, commentary, DB↔engine mapping)
- `app/data/seed/` — animal/environment seed data and loader
