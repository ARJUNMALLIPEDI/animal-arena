from __future__ import annotations


def test_list_animals_returns_seeded_roster(client):
    resp = client.get("/api/animals")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 30
    assert all("combat_attributes" in a for a in data)
    assert all("attribute_sources" in a for a in data)


def test_list_animals_filter_by_category(client):
    resp = client.get("/api/animals", params={"category": "reptile"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert all(a["category"] == "reptile" for a in data)


def test_list_animals_filter_by_habitat(client):
    resp = client.get("/api/animals", params={"habitat": "ocean"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert all("ocean" in a["habitats"] for a in data)


def test_search_animals_case_insensitive(client):
    resp = client.get("/api/animals", params={"search": "lion"})
    assert resp.status_code == 200
    names = [a["common_name"].lower() for a in resp.json()]
    assert any("lion" in n for n in names)


def test_get_single_animal(client):
    resp = client.get("/api/animals/african_lion")
    assert resp.status_code == 200
    assert resp.json()["id"] == "african_lion"


def test_get_missing_animal_returns_404(client):
    resp = client.get("/api/animals/not_a_real_animal")
    assert resp.status_code == 404


def test_environments_are_seeded(client):
    resp = client.get("/api/environments")
    assert resp.status_code == 200
    ids = {e["id"] for e in resp.json()}
    assert ids == {"savanna", "forest", "desert", "arctic", "ocean", "mountain", "open_plains"}
