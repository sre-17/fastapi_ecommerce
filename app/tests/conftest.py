from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
import pytest

from app import database, models, schemas, utils, oauth2
from app.main import app
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password} \
                            @{settings.database_hostname}/{settings.database_name}_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_products(session: Session):
    products_data = [{"name": "test product 1", "description": "a test description", "quantity": 4, "price": 34.4},
                     {"name": "test product 2", "description": "a test description",
                         "quantity": 4, "price": 34.4},
                     {"name": "test product 3", "description": "a test description", "quantity": 4, "price": 2}]

    products = list(map(
        lambda product: models.Product(**product), products_data))
    session.add_all(products)
    session.commit()

    products = session.query(models.Product).all()
    return products


@pytest.fixture
def test_user(session: Session):
    user_data = {"email": "testuser@test.com",
                 "password": "testhello"}
    new_user = models.User(
        email=user_data["email"], password=utils.hash_password(user_data["password"]))
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    user_data.update({"id": new_user.id})
    return user_data


@pytest.fixture
def token(test_user):
    token = oauth2.create_access_token({"user_id": test_user['id']})
    return token


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def add_to_cart(test_user, session: Session, test_products):
    new_item = models.Cart(
        product_id=test_products[0].id, user_id=test_user['id'])
    session.add(new_item)
    session.commit()
    return new_item
