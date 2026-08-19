from app.models.products import Product

def test_get_products(client):
    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_get_products(client):
    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_create_product(admin_client, test_category):
    response = admin_client.post(
        "/products/",
        json={
            "name": "Test Laptop",
            "price": 50000,
            "stock": 10,
            "category_id": test_category.id
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Laptop"
    assert data["price"] == 50000
    assert data["stock"] == 10
    assert data["category_id"] == test_category.id

def test_create_product_without_authentication(client, test_category):
    response = client.post(
        "/products/",
        json={
            "name": "Unauthorized Laptop",
            "price": 30000,
            "stock": 5,
            "category_id": test_category.id
        }
    )

    assert response.status_code == 401

def test_create_product_as_normal_user(user_client, test_category):
    response = user_client.post(
        "/products/",
        json={
            "name": "Normal User Laptop",
            "price": 30000,
            "stock": 5,
            "category_id": test_category.id
        }
    )

    assert response.status_code == 403

def test_update_product(
    admin_client,
    test_product
):

    response = admin_client.put(
        f"/products/{test_product.id}",
        json={
            "name": "Updated Product",
            "price": 30000,
            "stock": 20
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Product"
    assert data["price"] == 30000
    assert data["stock"] == 20

def test_update_product_as_normal_user(
    user_client,
    test_product
):

    response = user_client.put(
        f"/products/{test_product.id}",
        json={
            "name": "Blocked Update",
            "price": 10000,
            "stock": 1
        }
    )

    assert response.status_code == 403

def test_delete_product(
    admin_client,
    test_product,
    db_session
):

    product_id = test_product.id

    response = admin_client.delete(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    deleted_product = db_session.query(
        Product
    ).filter(
        Product.id == product_id
    ).first()

    assert deleted_product is None

def test_delete_product_as_normal_user(
    user_client,
    test_product
):

    response = user_client.delete(
        f"/products/{test_product.id}"
    )

    assert response.status_code == 403

def test_get_product_by_id(
    client,
    test_product,
    mock_product_redis
):

    mock_product_redis.get.return_value = None

    response = client.get(
        f"/products/{test_product.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_product.id
    assert data["name"] == test_product.name
    assert data["price"] == test_product.price
    assert data["stock"] == test_product.stock

def test_get_product_not_found(
    client,
    mock_product_redis
):

    mock_product_redis.get.return_value = None

    response = client.get(
        "/products/999999"
    )

    assert response.status_code == 404

