from fastapi.testclient import TestClient

from app.main import app


def test_order_creation_reduces_inventory_stock():
    with TestClient(app) as client:
        client.patch("/inventory/2", json={"available_quantity": 5})
        inventory_before = client.get("/inventory/2").json()["available_quantity"]

        order_response = client.post(
            "/orders",
            json={
                "customer_id": "customer-001",
                "items": [{"product_id": 2, "quantity": 2}],
            },
        )
        inventory_after = client.get("/inventory/2").json()["available_quantity"]

    assert order_response.status_code == 201
    order = order_response.json()
    assert order["status"] == "CONFIRMED"
    assert order["items"][0]["product_id"] == 2
    assert inventory_after == inventory_before - 2


def test_order_creation_rejects_insufficient_stock():
    with TestClient(app) as client:
        client.patch("/inventory/3", json={"available_quantity": 1})
        response = client.post(
            "/orders",
            json={
                "customer_id": "customer-002",
                "items": [{"product_id": 3, "quantity": 2}],
            },
        )

    assert response.status_code == 409
