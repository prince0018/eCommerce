from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def authenticated_headers(client: TestClient) -> dict[str, str]:
    email = f"cart-{uuid4().hex}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Cart User",
            "password": "strong-password",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "strong-password"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_authenticated_user_can_manage_cart():
    with TestClient(app) as client:
        headers = authenticated_headers(client)
        client.patch("/inventory/4", json={"available_quantity": 10})

        add_response = client.post(
            "/cart/items",
            json={"product_id": 4, "quantity": 2},
            headers=headers,
        )
        update_response = client.patch(
            "/cart/items/4",
            json={"quantity": 3},
            headers=headers,
        )
        remove_response = client.delete("/cart/items/4", headers=headers)
        empty_cart_response = client.get("/cart", headers=headers)

    assert add_response.status_code == 201
    assert add_response.json()["total_items"] == 2
    assert update_response.json()["total_items"] == 3
    assert remove_response.status_code == 204
    assert empty_cart_response.json()["items"] == []


def test_cart_rejects_quantity_above_available_stock():
    with TestClient(app) as client:
        headers = authenticated_headers(client)
        client.patch("/inventory/5", json={"available_quantity": 1})
        response = client.post(
            "/cart/items",
            json={"product_id": 5, "quantity": 2},
            headers=headers,
        )

    assert response.status_code == 409


def test_cart_checkout_creates_order_and_clears_cart():
    with TestClient(app) as client:
        headers = authenticated_headers(client)
        client.patch("/inventory/6", json={"available_quantity": 5})
        client.post(
            "/cart/items",
            json={"product_id": 6, "quantity": 2},
            headers=headers,
        )

        checkout_response = client.post("/cart/checkout", headers=headers)
        cart_response = client.get("/cart", headers=headers)

    assert checkout_response.status_code == 201
    assert checkout_response.json()["status"] == "CONFIRMED"
    assert cart_response.json()["items"] == []
