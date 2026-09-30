# Architecture

## System diagram

```mermaid
flowchart LR
    subgraph Frontend["Frontend — React + TypeScript + Vite"]
        Pages["Pages\n(Home / Bestiary / Tournament / Dashboard)"]
        Components["Components\n(battle, animals, charts, tournament, commentary)"]
        Hooks["Hooks\n(React Query)"]
        ApiClient["api/ client\n(typed axios wrappers)"]
        Store["Zustand store\n(matchup selection UI state)"]

        Pages --> Components
        Components --> Hooks
        Hooks --> ApiClient
        Components --> Store
    end

    subgraph Backend["Backend — FastAPI"]
        Routers["Routers\n(animals, environments, matchups,\ntournaments, commentary, stats)"]
        Schemas["Pydantic schemas\n(typed request/response, validation)"]
        Services["Services\n(matchup, tournament, commentary,\nDB<->engine mapper)"]
        Engine["simulation/ engine\n(pure Python + NumPy,\nzero framework deps)"]
        Models["SQLAlchemy models"]
        DB[("SQLite (dev) /\nPostgreSQL (prod)")]
        LLM["Anthropic API\n(commentary only)"]

        Routers --> Schemas
        Routers --> Services
        Services --> Engine
        Services --> Models
        Models --> DB
        Services --> LLM
    end

    ApiClient <-->|REST / JSON| Routers
```

## Why it's organized this way

**The simulation engine is isolated on purpose.** `backend/app/simulation/`
imports nothing from `app.models`, `app.routers`, `app.services`, or any web
framework. It operates entirely on plain dataclasses
(`AnimalProfile`, `EnvironmentProfile`, `CombatAttributes`). That is what lets
`tests/test_simulation_engine.py` unit test the actual combat math in
isolation, in milliseconds, with no database or HTTP server involved — and
it's the concrete proof that the matchup outcome comes from deterministic/
probabilistic simulation, not from asking an LLM who would win.

**The mapper is the only bridge between the DB and the engine.**
`app/services/mapper.py` converts a SQLAlchemy `Animal`/`Environment` row into
the engine's plain dataclasses. Nothing else touches both layers, so the
engine could be extracted into its own package with no changes.

**Services own business logic; routers stay thin.** Each router
(`app/routers/*.py`) does request validation (via Pydantic) and delegates to
a service function (`app/services/*.py`) that does the actual work —
building the engine call, persisting results, computing tournament brackets,
calling the LLM. This keeps HTTP concerns (status codes, request shape) out
of the logic that's actually worth unit testing.

**The frontend never embeds matchup logic.** Every component that needs data
goes through a hook in `src/hooks/`, which goes through a typed function in
`src/api/`, which goes through the one shared axios client
(`src/api/client.ts`). No component builds a URL, calls `fetch` directly, or
computes a win probability client-side — all of that is server-authoritative.

## Data flow for one matchup simulation

1. User picks two animals + an environment on the Home page; selections live
   in a Zustand store (`src/store/matchupStore.ts`).
2. `SIMULATE BATTLE` triggers `useSimulateMatchup()`, which POSTs a typed
   `SimulateRequest` to `/api/matchups/simulate`.
3. `routers/matchups.py` validates the request (Pydantic) and calls
   `services/matchup_service.simulate_matchup()`.
4. The service loads both `Animal` rows and the `Environment` row, maps them
   to engine dataclasses, resolves any what-if overrides/equalization, and
   calls `simulation.run_simulation()`.
5. The engine applies environment modifiers, runs N vectorized Monte Carlo
   encounters, and returns a `MatchupResult` (win counts, round stats, key
   factors).
6. The service persists a `Matchup` row and returns it as a typed
   `MatchupResultOut`.
7. The frontend renders the stylized battle animation, then the win
   probability bars, attribute radar chart, and outcome distribution chart —
   all sourced directly from that one response.
8. Optionally, the user requests AI commentary; that's a separate call to
   `/api/commentary` carrying the matchup's stored result, never the winner
   decision itself.

## Database

SQLite by default (`DATABASE_URL=sqlite:///./animal_arena.db`), created and
seeded automatically on first run. The schema avoids SQLite-only types
(JSON columns, string UUID primary keys, standard column types), so pointing
`DATABASE_URL` at a PostgreSQL instance instead
(`postgresql+psycopg://user:pass@host:5432/animal_arena`) requires no model
or migration changes — only installing a Postgres driver
(`pip install psycopg[binary]`).

Tables: `animals`, `environments`, `matchups`, `tournaments`,
`tournament_matches`, `commentary` (see `backend/app/models/`).
