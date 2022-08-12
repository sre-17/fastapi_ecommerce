from app.schemas import Product


def test_create_product(client):
    res = client.post("/products/", json={"name": "test product",
                      "description": "a nice description", "quantity": 2, "price": 34.3})
    product = Product(**res.json())
    assert res.status_code == 201
    assert product.name == "test product"


def test_get_all_products(client, test_products):
    res = client.get("/products/")
    assert res.status_code == 200


def test_get_one_product(client, test_products):
    res = client.get(f"/products/{test_products[0].id}/")
    assert res.status_code == 200


def test_update_product(client, test_products):
    res = client.put(f"/products/{test_products[0].id}", json={"name": "updated product",
                                                               "description": "a nice description updated", "quantity": 4, "price": 34.3})
    product = Product(**res.json())
    assert product.name == "updated product"
    assert product.description == "a nice description updated"
    assert product.quantity == 4


def test_delete_product(client, test_products):
    res = client.delete(f"/products/{test_products[0].id}")
    assert res.status_code == 204
