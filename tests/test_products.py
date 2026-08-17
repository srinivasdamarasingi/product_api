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