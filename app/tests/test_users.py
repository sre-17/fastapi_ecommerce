from app import schemas, oauth2
import pytest


def test_user_login(client, test_user):
    response = client.post(
        "/login", data={"username": test_user['email'], "password": test_user['password']})
    assert response.status_code == 200
    token = schemas.Token(**response.json())
    assert token.token_type == "bearer"


@pytest.mark.parametrize("username, password", [
    ("testuser@test.com", "password"),
    ("testuser1@test.com", "password"),
    ("itestuser@test.com", "passworddddd"),
])
def test_invalid_user_login(client, test_user, username, password):
    response = client.post(
        "/login", data={"username": username, "password": password})
    assert response.status_code == 403


def test_token_validity(client, test_user):
    response = client.post(
        "/login", data={"username": test_user['email'], "password": test_user['password']})

    token = schemas.Token(**response.json())
    payload = oauth2.jwt.decode(
        token.access_token, oauth2.SECRET_KEY, oauth2.ALGORITHM)
    assert payload.get("user_id") == test_user['id']
