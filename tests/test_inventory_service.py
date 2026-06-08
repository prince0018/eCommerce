from fastapi.testclient import TestClient

from app.main import app


def test_inventory_can_reduce_stock_for_purchase():
    with TestClient(app) as client:
        client.patch("/inventory/1", json={"available_quantity": 5})
        inventory_response = client.get("/inventory/1")
        before = inventory_response.json()["available_quantity"]

        purchase_response = client.post("/inventory/1/purchase", json={"quantity": 1})

    assert purchase_response.status_code == 200
    body = purchase_response.json()
    assert body["available_quantity"] == before - 1
    assert body["sold_quantity"] >= 1


def test_inventory_rejects_purchase_when_stock_is_not_enough():
    with TestClient(app) as client:
        response = client.post("/inventory/1/purchase", json={"quantity": 999999})

    assert response.status_code == 409
