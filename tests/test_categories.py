def test_create_category(admin_client):

    response = admin_client.post(
        "/categories/",
        json={
            "name": "Electronics"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Electronics"
    assert "id" in data

def test_list_categories(
    client,
    test_category
):

    response = client.get(
        "/categories/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        category["id"] == test_category.id
        for category in data
    )

def test_get_category_by_id(
    client,
    test_category
):

    response = client.get(
        f"/categories/{test_category.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_category.id
    assert data["name"] == test_category.name

def test_get_category_not_found(client):

    response = client.get(
        "/categories/999999"
    )

    assert response.status_code == 404

def test_create_duplicate_category(
    admin_client,
    test_category
):

    response = admin_client.post(
        "/categories/",
        json={
            "name": test_category.name
        }
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Category already exists"
    )