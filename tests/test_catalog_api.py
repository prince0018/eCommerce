from fastapi.testclient import TestClient

from app.main import app


def test_list_products_returns_seeded_catalog():
    with TestClient(app) as client:
        response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 40
    assert any(product["name"] == "iPhone 15" for product in body["products"])


def test_get_missing_product_returns_404():
    with TestClient(app) as client:
        response = client.get("/products/999999")

    assert response.status_code == 404


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
