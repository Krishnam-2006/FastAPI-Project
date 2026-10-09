# Helpers


async def _create_user_and_token(
    client,
    username="testuser",
    email="test@example.com",
):
    registration = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": "password123",
        },
    )
    assert registration.status_code in (200, 201), registration.text

    login = await client.post(
        "/api/users/token",
        data={
            "username": email,
            "password": "password123",
        },
    )
    assert login.status_code == 200, login.text

    return login.json()["access_token"]


async def _create_post(
    client,
    token,
    title="Test Post",
    content="This is a test post.",
):
    return await client.post(
        "/api/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": title, "content": content},
    )


# CREATE POST


async def test_create_post(client):
    token = await _create_user_and_token(client)

    response = await _create_post(client, token)

    assert response.status_code == 201
    assert response.json()["title"] == "Test Post"
    assert response.json()["content"] == "This is a test post."
    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert user_response.status_code == 200
    assert response.json()["user_id"] == user_response.json()["id"]


async def test_create_post_unauthorized(client):
    response = await client.post(
        "/api/posts",
        json={"title": "Test", "content": "Test content"},
    )
    assert response.status_code == 401


async def test_create_post_invalid_data(client):
    token = await _create_user_and_token(client)

    response = await client.post(
        "/api/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Missing title"},
    )
    assert response.status_code == 422


async def test_create_post_empty_title(client):
    token = await _create_user_and_token(client)

    response = await _create_post(
        client,
        token,
        title="",
        content="Test content",
    )
    assert response.status_code == 422


# GET ALL POSTS


async def test_get_posts(client):
    token = await _create_user_and_token(client)
    await _create_post(client, token)

    response = await client.get("/api/posts")

    assert response.status_code == 200
    assert len(response.json()["posts"]) == 1
    assert response.json()["total"] == 1


async def test_get_posts_empty(client):
    response = await client.get("/api/posts")

    assert response.status_code == 200
    assert response.json()["posts"] == []
    assert response.json()["total"] == 0


async def test_get_posts_has_more(client):
    token = await _create_user_and_token(client)

    for i in range(3):
        await _create_post(
            client,
            token,
            title=f"Post {i}",
        )

    response = await client.get("/api/posts?skip=0&limit=2")

    assert response.status_code == 200
    assert response.json()["has_more"] is True


async def test_get_posts_last_page_has_no_more(client):
    token = await _create_user_and_token(client)

    for i in range(3):
        await _create_post(
            client,
            token,
            title=f"Post {i}",
        )

    response = await client.get("/api/posts?skip=2&limit=1")

    assert response.status_code == 200
    assert len(response.json()["posts"]) == 1
    assert response.json()["has_more"] is False


async def test_get_posts_pagination(client):
    token = await _create_user_and_token(client)

    await _create_post(client, token, title="Post One")
    await _create_post(client, token, title="Post Two")
    await _create_post(client, token, title="Post Three")

    response = await client.get("/api/posts?skip=1&limit=1")

    assert response.status_code == 200
    assert len(response.json()["posts"]) == 1
    assert response.json()["posts"][0]["title"] == "Post Two"


async def test_get_posts_invalid_skip(client):
    response = await client.get("/api/posts?skip=-1")

    assert response.status_code == 422


async def test_get_posts_invalid_limit(client):
    response = await client.get("/api/posts?limit=0")

    assert response.status_code == 422


async def test_get_posts_limit_too_high(client):
    response = await client.get("/api/posts?limit=101")

    assert response.status_code == 422


# GET SINGLE POST


async def test_get_post(client):
    token = await _create_user_and_token(client)
    created = await _create_post(client, token)
    post_id = created.json()["id"]

    response = await client.get(f"/api/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Test Post"


async def test_get_post_not_found(client):
    response = await client.get("/api/posts/999")

    assert response.status_code == 404


# PUT POST


async def test_update_post_full(client):
    token = await _create_user_and_token(client)
    created = await _create_post(client, token)
    post_id = created.json()["id"]

    response = await client.put(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Title",
            "content": "Updated Content",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Updated Content"

    check = await client.get(f"/api/posts/{post_id}")
    assert check.status_code == 200
    assert check.json()["title"] == "Updated Title"
    assert check.json()["content"] == "Updated Content"


async def test_update_post_full_not_found(client):
    token = await _create_user_and_token(client)

    response = await client.put(
        "/api/posts/999",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated", "content": "Updated content"},
    )

    assert response.status_code == 404


async def test_update_post_full_not_authorized(client):
    author_token = await _create_user_and_token(client, "author", "author@example.com")
    other_token = await _create_user_and_token(client, "other", "other@example.com")

    created = await _create_post(client, author_token, title="Original Title")
    post_id = created.json()["id"]

    response = await client.put(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "Changed Title", "content": "Changed content"},
    )

    assert response.status_code == 403

    check = await client.get(f"/api/posts/{post_id}")
    assert check.status_code == 200
    assert check.json()["title"] == "Original Title"


async def test_update_post_full_unauthorized(client):
    response = await client.put(
        "/api/posts/999",
        json={"title": "Updated", "content": "Updated content"},
    )

    assert response.status_code == 401


async def test_update_post_full_missing_field(client):
    token = await _create_user_and_token(client)
    created = await _create_post(client, token)
    post_id = created.json()["id"]

    response = await client.put(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Title"},
    )

    assert response.status_code == 422


# PATCH POST


async def test_update_post_partial(client):
    token = await _create_user_and_token(client)
    created = await _create_post(
        client,
        token,
        title="Original Title",
        content="Original Content",
    )
    post_id = created.json()["id"]

    response = await client.patch(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

    check = await client.get(f"/api/posts/{post_id}")
    assert check.status_code == 200
    assert check.json()["title"] == "Updated Title"
    assert check.json()["content"] == "Original Content"


async def test_update_post_partial_not_found(client):
    token = await _create_user_and_token(client)

    response = await client.patch(
        "/api/posts/999",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated"},
    )

    assert response.status_code == 404


async def test_update_post_partial_not_authorized(client):
    author_token = await _create_user_and_token(client, "author", "author@example.com")
    other_token = await _create_user_and_token(client, "other", "other@example.com")

    created = await _create_post(client, author_token, title="Original Title")
    post_id = created.json()["id"]

    response = await client.patch(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "Changed Title"},
    )

    assert response.status_code == 403

    check = await client.get(f"/api/posts/{post_id}")
    assert check.status_code == 200
    assert check.json()["title"] == "Original Title"


async def test_update_post_partial_unauthorized(client):
    response = await client.patch(
        "/api/posts/999",
        json={"title": "Updated"},
    )

    assert response.status_code == 401


# DELETE POST


async def test_delete_post(client):
    token = await _create_user_and_token(client)
    created = await _create_post(client, token)
    post_id = created.json()["id"]

    response = await client.delete(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    check = await client.get(f"/api/posts/{post_id}")
    assert check.status_code == 404


async def test_delete_post_not_found(client):
    token = await _create_user_and_token(client)

    response = await client.delete(
        "/api/posts/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


async def test_delete_post_not_authorized(client):
    author_token = await _create_user_and_token(client, "author", "author@example.com")
    other_token = await _create_user_and_token(client, "other", "other@example.com")

    created = await _create_post(client, author_token, title="Original Title")
    post_id = created.json()["id"]

    response = await client.delete(
        f"/api/posts/{post_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 403

    check = await client.get(f"/api/posts/{post_id}")
    assert check.status_code == 200
    assert check.json()["title"] == "Original Title"


async def test_delete_post_unauthorized(client):
    response = await client.delete("/api/posts/999")

    assert response.status_code == 401
