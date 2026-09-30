from __future__ import annotations


def _make_matchup(client):
    return client.post(
        "/api/matchups/simulate",
        json={"animal_a_id": "african_lion", "animal_b_id": "grizzly_bear", "environment_id": "open_plains", "num_simulations": 1000, "seed": 3},
    ).json()


def test_commentary_falls_back_without_api_key(client):
    # conftest sets ANTHROPIC_API_KEY="" so this must not attempt a real
    # network call, and must never invent numbers not in the simulation data.
    matchup = _make_matchup(client)
    resp = client.post("/api/commentary", json={"matchup_id": matchup["id"], "style": "scientific"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated_by_llm"] is False
    assert str(round(matchup["avg_rounds"], 1)) in data["text"] or "%" in data["text"]


def test_commentary_is_cached(client):
    matchup = _make_matchup(client)
    r1 = client.post("/api/commentary", json={"matchup_id": matchup["id"], "style": "sports"}).json()
    r2 = client.post("/api/commentary", json={"matchup_id": matchup["id"], "style": "sports"}).json()
    assert r1["text"] == r2["text"]
    assert r1["created_at"] == r2["created_at"]


def test_commentary_force_refresh_regenerates(client):
    matchup = _make_matchup(client)
    r1 = client.post("/api/commentary", json={"matchup_id": matchup["id"], "style": "documentary"}).json()
    r2 = client.post(
        "/api/commentary", json={"matchup_id": matchup["id"], "style": "documentary", "force_refresh": True}
    ).json()
    assert r1["created_at"] != r2["created_at"]


def test_commentary_missing_matchup_returns_404(client):
    resp = client.post("/api/commentary", json={"matchup_id": "does-not-exist", "style": "scientific"})
    assert resp.status_code == 404
