from __future__ import annotations


def test_create_and_resolve_tournament(client):
    payload = {
        "name": "Test Cup",
        "environment_id": "savanna",
        "animal_ids": [
            "african_lion", "grizzly_bear", "siberian_tiger", "nile_crocodile",
        ],
        "num_simulations": 1000,
        "seed": 1,
    }
    created = client.post("/api/tournaments", json=payload).json()
    assert created["status"] == "pending"
    assert len(created["matches"]) == 3  # 2 semifinal + 1 final for 4 animals

    resp = client.post(f"/api/tournaments/{created['id']}/advance", params={"num_simulations": 1000, "seed": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["champion_id"] in payload["animal_ids"]
    for match in data["matches"]:
        assert match["winner_id"] is not None
        assert match["matchup"] is not None


def test_tournament_requires_power_of_two_animals(client):
    resp = client.post(
        "/api/tournaments",
        json={
            "name": "Bad Cup",
            "environment_id": "savanna",
            "animal_ids": ["african_lion", "grizzly_bear", "siberian_tiger"],
        },
    )
    assert resp.status_code == 422


def test_tournament_rejects_duplicate_animals(client):
    resp = client.post(
        "/api/tournaments",
        json={
            "name": "Dup Cup",
            "environment_id": "savanna",
            "animal_ids": ["african_lion", "african_lion", "grizzly_bear", "siberian_tiger"],
        },
    )
    assert resp.status_code == 422


def test_tournament_unknown_animal_returns_404(client):
    resp = client.post(
        "/api/tournaments",
        json={
            "name": "Ghost Cup",
            "environment_id": "savanna",
            "animal_ids": ["african_lion", "not_real", "grizzly_bear", "siberian_tiger"],
        },
    )
    assert resp.status_code == 404


def test_get_missing_tournament_returns_404(client):
    resp = client.get("/api/tournaments/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
