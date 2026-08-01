def test_create_and_list_users(client):
    create = client.post("/api/v1/users/", json={"name": "Ada", "age": 36})
    assert create.status_code == 201
    body = create.json()
    assert body["name"] == "Ada"
    assert body["age"] == 36
    assert "id" in body

    listing = client.get("/api/v1/users/")
    assert listing.status_code == 200
    users = listing.json()
    assert len(users) == 1
    assert users[0]["name"] == "Ada"


def test_get_update_delete_user(client):
    created = client.post("/api/v1/users/", json={"name": "Grace", "age": 40}).json()
    user_id = created["id"]

    got = client.get(f"/api/v1/users/{user_id}")
    assert got.status_code == 200
    assert got.json()["name"] == "Grace"

    updated = client.put(f"/api/v1/users/{user_id}", json={"name": "Hopper", "age": 41})
    assert updated.status_code == 200
    assert updated.json() == {"id": user_id, "name": "Hopper", "age": 41}

    deleted = client.delete(f"/api/v1/users/{user_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/users/{user_id}")
    assert missing.status_code == 404


def test_get_user_not_found(client):
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
