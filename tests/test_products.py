from app.models.products import Product
import json
from unittest.mock import patch, mock_open

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


def test_get_product_from_cache(
    client,
    test_product,
    mock_product_redis
):

    cached_product = {
        "id": test_product.id,
        "name": test_product.name,
        "price": test_product.price,
        "stock": test_product.stock,
        "category_id": test_product.category_id
    }

    mock_product_redis.get.return_value = json.dumps(
        cached_product
    )

    response = client.get(
        f"/products/{test_product.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_product.id

    mock_product_redis.get.assert_called_once()

def test_update_nonexistent_product(
    admin_client
):

    response = admin_client.put(
        "/products/999999",
        json={
            "name": "Invalid",
            "price": 100,
            "stock": 1
        }
    )

    assert response.status_code == 404

def test_delete_nonexistent_product(
    admin_client
):

    response = admin_client.delete(
        "/products/999999"
    )

    assert response.status_code == 404

def test_search_products(
    client,
    test_product
):

    response = client.get(
        "/products/search",
        params={
            "keyword": "Test"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        product["id"] == test_product.id
        for product in data
    )

def test_filter_products(
    client,
    test_product,
    test_category
):

    response = client.get(
        "/products/filter",
        params={
            "category_id": test_category.id,
            "min_price": 20000,
            "max_price": 30000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        product["id"] == test_product.id
        for product in data
    )

def test_sort_products_ascending(
    client,
    db_session,
    test_category
):

    product1 = Product(
        name="Cheap Product",
        price=100,
        stock=10,
        category_id=test_category.id
    )

    product2 = Product(
        name="Expensive Product",
        price=500,
        stock=10,
        category_id=test_category.id
    )

    db_session.add_all([
        product1,
        product2
    ])

    db_session.commit()

    response = client.get(
        "/products/sort",
        params={
            "order": "asc"
        }
    )

    assert response.status_code == 200

    data = response.json()

    prices = [
        product["price"]
        for product in data
    ]

    assert prices == sorted(prices)

def test_sort_products_descending(
    client,
    db_session,
    test_category
):

    product1 = Product(
        name="Cheap Product",
        price=100,
        stock=10,
        category_id=test_category.id
    )

    product2 = Product(
        name="Expensive Product",
        price=500,
        stock=10,
        category_id=test_category.id
    )

    db_session.add_all([
        product1,
        product2
    ])

    db_session.commit()

    response = client.get(
        "/products/sort",
        params={
            "order": "desc"
        }
    )

    assert response.status_code == 200

    data = response.json()

    prices = [
        product["price"]
        for product in data
    ]

    assert prices == sorted(
        prices,
        reverse=True
    )

def test_paginate_products(
    client,
    db_session,
    test_category
):

    for number in range(10):

        db_session.add(
            Product(
                name=f"Product {number}",
                price=100 + number,
                stock=10,
                category_id=test_category.id
            )
        )

    db_session.commit()

    response = client.get(
        "/products/paginate",
        params={
            "page": 1,
            "size": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5

def test_upload_product_image(
    admin_client,
    test_product
):

    with patch(
        "app.routers.products.uuid.uuid4",
        return_value="test-uuid"
    ), patch(
        "builtins.open",
        mock_open()
    ), patch(
        "app.routers.products.shutil.copyfileobj"
    ) as mock_copy:

        response = admin_client.post(
            f"/products/{test_product.id}/image",
            files={
                "file": (
                    "product.png",
                    b"fake-image-content",
                    "image/png"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_product.id

    assert data["image_path"] == (
        "uploads/products/"
        "test-uuid_product.png"
    )

    mock_copy.assert_called_once()

def test_upload_image_product_not_found(
    admin_client
):

    response = admin_client.post(
        "/products/999999/image",
        files={
            "file": (
                "product.png",
                b"fake-image-content",
                "image/png"
            )
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Product not found"
    )

def test_upload_image_without_authentication(
    client,
    test_product
):

    response = client.post(
        f"/products/{test_product.id}/image",
        files={
            "file": (
                "product.png",
                b"fake-image-content",
                "image/png"
            )
        }
    )

    assert response.status_code == 401

def test_upload_image_as_normal_user(
    user_client,
    test_product
):

    response = user_client.post(
        f"/products/{test_product.id}/image",
        files={
            "file": (
                "product.png",
                b"fake-image-content",
                "image/png"
            )
        }
    )

    assert response.status_code == 403

def test_upload_image_missing_file(
    admin_client,
    test_product
):

    response = admin_client.post(
        f"/products/{test_product.id}/image"
    )

    assert response.status_code == 422

def test_upload_invalid_image_type(
    admin_client,
    test_product
):

    response = admin_client.post(
        f"/products/{test_product.id}/image",
        files={
            "file": (
                "malware.exe",
                b"fake executable",
                "application/octet-stream"
            )
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid image type"
    )

def test_upload_invalid_extension(
    admin_client,
    test_product
):

    response = admin_client.post(
        f"/products/{test_product.id}/image",
        files={
            "file": (
                "script.php",
                b"fake image",
                "image/png"
            )
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid file extension"
    )

def test_upload_image_too_large(
    admin_client,
    test_product
):

    large_file = b"x" * (
        5 * 1024 * 1024 + 1
    )

    response = admin_client.post(
        f"/products/{test_product.id}/image",
        files={
            "file": (
                "large.png",
                large_file,
                "image/png"
            )
        }
    )

    assert response.status_code == 413

    assert response.json()["detail"] == (
        "File too large"
    )

def test_upload_sanitizes_filename(
    admin_client,
    test_product
):

    with patch(
        "app.routers.products.uuid.uuid4",
        return_value="safe-uuid"
    ), patch(
        "builtins.open",
        mock_open()
    ), patch(
        "app.routers.products.shutil.copyfileobj"
    ):

        response = admin_client.post(
            f"/products/{test_product.id}/image",
            files={
                "file": (
                    "../../evil.png",
                    b"fake-image",
                    "image/png"
                )
            }
        )

    assert response.status_code == 200

    image_path = response.json()[
        "image_path"
    ]

    assert ".." not in image_path

    assert image_path == (
        "uploads/products/"
        "safe-uuid_evil.png"
    )