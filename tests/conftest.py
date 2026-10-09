import os

# Force the application database to use the isolated test database
# before importing app.main or app.database.
TEST_DB_PASSWORD = os.getenv(
    "TEST_DB_PASSWORD",
    "test_password",
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg://postgres:{TEST_DB_PASSWORD}"
    "@postgres:5432/product_test_db",
)

from sqlalchemy.engine import make_url

parsed_test_url = make_url(TEST_DATABASE_URL)

if (
    parsed_test_url.host != "postgres"
    or parsed_test_url.database != "product_test_db"
):
    raise RuntimeError(
        "Unsafe test database configuration"
    )

os.environ["CONFIG_SOURCE"] = "environment"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.category import Category
from app.models.user import User
from app.security import hash_password, create_access_token
from app.models.products import Product
from unittest.mock import MagicMock

# ============================================================
# TEST DATABASE
# ============================================================

test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=True
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


# ============================================================
# CREATE TEST DATABASE TABLES
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


# ============================================================
# CLEAN DATABASE BEFORE EVERY TEST
# ============================================================

@pytest.fixture(autouse=True)
def clean_database():

    with test_engine.begin() as connection:

        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())


# ============================================================
# DATABASE SESSION
# ============================================================

@pytest.fixture
def db_session():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.rollback()
        db.close()


# ============================================================
# TEST CATEGORY
# ============================================================

@pytest.fixture
def test_category(db_session):

    category = Category(
        name="Test Category"
    )

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    return category


# ============================================================
# TEST ADMIN USER
# ============================================================

@pytest.fixture
def test_admin(db_session):

    admin = User(
        username="test_admin",
        email="test_admin@example.com",
        hashed_password=hash_password(
            "TestPassword123!"
        ),
        is_active=True,
        is_admin=True
    )

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


# ============================================================
# TEST NORMAL USER
# ============================================================

@pytest.fixture
def test_user(db_session):

    user = User(
        username="test_user",
        email="test_user@example.com",
        hashed_password=hash_password(
            "TestPassword123!"
        ),
        is_active=True,
        is_admin=False
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


# ============================================================
# NORMAL CLIENT - NO AUTHENTICATION
# ============================================================

@pytest.fixture
def client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:

        yield test_client

    app.dependency_overrides.clear()


# ============================================================
# ADMIN CLIENT
# ============================================================

@pytest.fixture
def admin_client(
    db_session,
    test_admin
):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    token = create_access_token(
        {
            "sub": test_admin.email
        }
    )

    with TestClient(app) as test_client:

        test_client.headers.update({
            "Authorization": f"Bearer {token}"
        })

        yield test_client

    app.dependency_overrides.clear()


# ============================================================
# NORMAL USER CLIENT
# ============================================================

@pytest.fixture
def user_client(
    db_session,
    test_user
):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    token = create_access_token(
        {
            "sub": test_user.email
        }
    )

    with TestClient(app) as test_client:

        test_client.headers.update({
            "Authorization": f"Bearer {token}"
        })

        yield test_client

    app.dependency_overrides.clear()


# ============================================================
# CLIENT FOR TESTING SERVER ERRORS
# ============================================================

@pytest.fixture
def error_client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(
        app,
        raise_server_exceptions=False
    ) as test_client:

        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def test_product(db_session, test_category):

    product = Product(
        name="Test Product",
        price=25000,
        stock=10,
        category_id=test_category.id
    )

    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    return product

@pytest.fixture
def mock_redis(monkeypatch):
    from unittest.mock import MagicMock

    mock = MagicMock()

    monkeypatch.setattr(
        "app.services.redis_service.redis_client",
        mock
    )

    return mock


@pytest.fixture
def mock_product_redis(monkeypatch):

    mock_redis = MagicMock()

    monkeypatch.setattr(
        "app.crud.product.redis_client",
        mock_redis
    )

    return mock_redis
