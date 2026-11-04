import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app("sqlite:///:memory:")
    return app.test_client()


def meal(**overrides):
    data = {
        "name": "Salada",
        "description": "Salada com frango",
        "date_time": "2026-11-04T12:30:00",
        "is_on_diet": True,
    }
    data.update(overrides)
    return data


def test_create_and_get(client):
    res = client.post("/meals", json=meal())
    assert res.status_code == 201
    meal_id = res.get_json()["meal"]["id"]

    res = client.get(f"/meals/{meal_id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Salada"


def test_create_invalid(client):
    res = client.post("/meals", json={"name": "Sem resto"})
    assert res.status_code == 400


def test_list(client):
    client.post("/meals", json=meal())
    client.post("/meals", json=meal(name="Pizza", is_on_diet=False))
    res = client.get("/meals")
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_update(client):
    meal_id = client.post("/meals", json=meal()).get_json()["meal"]["id"]
    res = client.put(f"/meals/{meal_id}", json={"name": "Salada Caesar", "is_on_diet": False})
    assert res.status_code == 200
    body = res.get_json()["meal"]
    assert body["name"] == "Salada Caesar"
    assert body["is_on_diet"] is False
    assert body["description"] == "Salada com frango"


def test_delete(client):
    meal_id = client.post("/meals", json=meal()).get_json()["meal"]["id"]
    assert client.delete(f"/meals/{meal_id}").status_code == 200
    assert client.get(f"/meals/{meal_id}").status_code == 404


def test_not_found(client):
    assert client.get("/meals/999").status_code == 404
    assert client.put("/meals/999", json={"name": "x"}).status_code == 404
    assert client.delete("/meals/999").status_code == 404


def test_metrics(client):
    for i, on_diet in enumerate([True, True, False, True]):
        client.post("/meals", json=meal(date_time=f"2026-11-0{i + 1}T12:00:00", is_on_diet=on_diet))
    res = client.get("/meals/metrics").get_json()
    assert res == {
        "total_meals": 4,
        "meals_on_diet": 3,
        "meals_off_diet": 1,
        "best_sequence_on_diet": 2,
    }
