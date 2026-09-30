from __future__ import annotations


def test_simulate_matchup_happy_path(client):
    payload = {
        "animal_a_id": "african_lion",
        "animal_b_id": "grizzly_bear",
        "environment_id": "open_plains",
        "num_simulations": 2000,
        "seed": 42,
    }
    resp = client.post("/api/matchups/simulate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["animal_a_wins"] + data["animal_b_wins"] + data["draws"] == 2000
    assert 0 <= data["win_pct_a"] <= 100
    assert 0 <= data["win_pct_b"] <= 100
    assert len(data["key_factors"]) > 0
    assert "id" in data and "created_at" in data


def test_simulate_is_reproducible_with_same_seed(client):
    payload = {
        "animal_a_id": "leopard",
        "animal_b_id": "jaguar",
        "environment_id": "forest",
        "num_simulations": 1500,
        "seed": 123,
    }
    r1 = client.post("/api/matchups/simulate", json=payload).json()
    r2 = client.post("/api/matchups/simulate", json=payload).json()
    assert r1["animal_a_wins"] == r2["animal_a_wins"]
    assert r1["avg_rounds"] == r2["avg_rounds"]


def test_simulate_unknown_animal_returns_404(client):
    resp = client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "dragon", "animal_b_id": "grizzly_bear", "environment_id": "open_plains"},
    )
    assert resp.status_code == 404


def test_simulate_unknown_environment_returns_404(client):
    resp = client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "african_lion", "animal_b_id": "grizzly_bear", "environment_id": "volcano"},
    )
    assert resp.status_code == 404


def test_simulate_same_animal_returns_422(client):
    resp = client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "african_lion", "animal_b_id": "african_lion", "environment_id": "open_plains"},
    )
    assert resp.status_code == 422


def test_simulate_num_simulations_out_of_bounds_returns_422(client):
    resp = client.post(
        "/api/matchups/simulate",
        json={
            "animal_a_id": "african_lion",
            "animal_b_id": "grizzly_bear",
            "environment_id": "open_plains",
            "num_simulations": 999999,
        },
    )
    assert resp.status_code == 422


def test_what_if_equalize_narrows_the_gap(client):
    baseline_payload = {
        "animal_a_id": "african_elephant",
        "animal_b_id": "wolverine",
        "environment_id": "open_plains",
        "num_simulations": 3000,
        "seed": 5,
    }
    baseline = client.post("/api/matchups/simulate", json=baseline_payload).json()

    equalized_payload = {**baseline_payload, "equalize_attributes": ["size", "strength"]}
    equalized = client.post("/api/matchups/simulate", json=equalized_payload).json()

    assert equalized["win_pct_a"] < baseline["win_pct_a"]
    assert equalized["what_if_overrides"]["equalize_attributes"] == ["size", "strength"]


def test_what_if_direct_override(client):
    payload = {
        "animal_a_id": "chimpanzee",
        "animal_b_id": "gorilla",
        "environment_id": "forest",
        "num_simulations": 2000,
        "seed": 2,
        "overrides_a": {"strength": 95},
    }
    resp = client.post("/api/matchups/simulate", json=payload)
    assert resp.status_code == 200
    assert resp.json()["effective_attributes_a"]["strength"] == 95


def test_get_matchup_history(client):
    client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "cheetah", "animal_b_id": "hyena_placeholder", "environment_id": "savanna"},
    )  # intentionally invalid, should not appear in history
    client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "cheetah", "animal_b_id": "spotted_hyena", "environment_id": "savanna", "num_simulations": 500},
    )
    resp = client.get("/api/matchups", params={"limit": 5})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_single_matchup_round_trip(client):
    created = client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "orca", "animal_b_id": "great_white_shark", "environment_id": "ocean", "num_simulations": 1000},
    ).json()
    resp = client.get(f"/api/matchups/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_missing_matchup_returns_404(client):
    resp = client.get("/api/matchups/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
