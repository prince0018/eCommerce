from fastapi.testclient import TestClient

from app.main import app


def test_list_products_returns_seeded_catalog():
    with TestClient(app) as client:
        response = client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 190
    assert any(
        product["name"] == "Essence Mascara Lash Princess"
        and product["currency"] == "INR"
        and product["thumbnail"]
        for product in body["products"]
    )


def test_get_missing_product_returns_404():
    with TestClient(app) as client:
        response = client.get("/products/999999")

    assert response.status_code == 404


def test_product_detail_contains_dummyjson_images_and_inr_conversion():
    with TestClient(app) as client:
        response = client.get("/products/1")

    assert response.status_code == 200
    product = response.json()
    assert product["price"] == "954"
    assert product["currency"] == "INR"
    assert product["source_price_usd"] == "9.99"
    assert product["thumbnail"].startswith("https://cdn.dummyjson.com/")
    assert product["images"]
    assert product["source_data"]["title"] == "Essence Mascara Lash Princess"
