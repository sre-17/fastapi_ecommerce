from app import schemas


def test_add_to_cart(authorized_client, test_products):
    response = authorized_client.post(
        "/cart/", json={"product_id": test_products[0].id, "add": "true"})
    assert response.status_code == 200


def test_get_cart_items(authorized_client, add_to_cart):
    response = authorized_client.get("/cart/")
    cart_response = schemas.CartOut(**response.json())
    assert add_to_cart.user_id == cart_response.user_id
    assert add_to_cart.product_id == cart_response.product_id
