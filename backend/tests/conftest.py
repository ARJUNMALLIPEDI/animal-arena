from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    # Point the app at an isolated, throwaway SQLite file before any app
    # module is imported, so app.core.config.get_settings() (which is
    # lru_cached) picks up the test database rather than the dev one.
    db_path = tmp_path_factory.mktemp("db") / "test_animal_arena.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["ANTHROPIC_API_KEY"] = ""  # force the deterministic commentary fallback in tests

    from app.main import app  # imported here, after env vars are set

    with TestClient(app) as test_client:
        yield test_client
