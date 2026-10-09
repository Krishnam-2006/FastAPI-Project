# tests/test_users.py

# Helpers used by the user and post tests


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
    assert registration.status_code == 201, registration.text

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


# CREATE USER


async def test_create_user(client):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert "password" not in response.json()
    assert all("password" not in key.lower() for key in response.json())


async def test_create_user_duplicate_username(client):
    await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "first@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "second@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


async def test_create_user_duplicate_email(client):
    await client.post(
        "/api/users",
        json={
            "username": "user1",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/users",
        json={
            "username": "user2",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


# LOGIN


async def test_login_for_access_token(client):
    await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_login_for_access_token_wrong_password(client):
    await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


# CURRENT USER


async def test_get_current_user(client):
    token = await _create_user_and_token(client)

    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


async def test_get_current_user_unauthorized(client):
    response = await client.get("/api/users/me")

    assert response.status_code == 401


# FORGOT AND RESET PASSWORD


async def test_forgot_password(client, mock_send_email):
    await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/users/forgot-password",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 202
    mock_send_email.assert_called_once()


async def test_reset_password(client, mock_send_email):
    await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    await client.post(
        "/api/users/forgot-password",
        json={"email": "test@example.com"},
    )

    token = mock_send_email.call_args.kwargs["token"]

    response = await client.post(
        "/api/users/reset-password",
        json={
            "token": token,
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Password reset successfully. You can now log in with your new password."
    )

    new_login = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "newpassword123",
        },
    )
    assert new_login.status_code == 200

    old_login = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )
    assert old_login.status_code == 401


async def test_reset_password_invalid_token(client):
    response = await client.post(
        "/api/users/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 400


async def test_forgot_password_unknown_email(client, mock_send_email):
    response = await client.post(
        "/api/users/forgot-password",
        json={"email": "unknown@example.com"},
    )

    assert response.status_code == 202
    mock_send_email.assert_not_called()


# CHANGE PASSWORD


async def test_change_password(client):
    token = await _create_user_and_token(client)

    response = await client.patch(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "password123",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    new_login = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "newpassword123",
        },
    )
    assert new_login.status_code == 200

    old_login = await client.post(
        "/api/users/token",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )
    assert old_login.status_code == 401


async def test_change_password_wrong_current_password(client):
    token = await _create_user_and_token(client)

    response = await client.patch(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect"


async def test_change_password_unauthorized(client):
    response = await client.patch(
        "/api/users/me/password",
        json={
            "current_password": "password123",
            "new_password": "newpassword123",
        },
    )

    assert response.status_code == 401


# GET USER


async def test_get_user(client):
    create_response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    user_id = create_response.json()["id"]

    response = await client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


async def test_get_user_not_found(client):
    response = await client.get("/api/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# GET USER POSTS


async def test_get_user_posts(client):
    create_response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    user_id = create_response.json()["id"]

    response = await client.get(f"/api/users/{user_id}/posts")

    assert response.status_code == 200
    assert response.json()["total"] == 0


async def test_get_user_posts_with_posts(client):
    token1 = await _create_user_and_token(client, "user1", "user1@example.com")
    token2 = await _create_user_and_token(client, "user2", "user2@example.com")

    post1 = await _create_post(client, token1, title="User One Post")
    post2 = await _create_post(client, token2, title="User Two Post")

    assert post1.status_code == 201
    assert post2.status_code == 201

    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token1}"},
    )
    user_id = user_response.json()["id"]

    response = await client.get(f"/api/users/{user_id}/posts")

    assert response.status_code == 200
    assert response.json()["total"] == 1

    titles = [post["title"] for post in response.json()["posts"]]
    assert titles == ["User One Post"]


async def test_get_user_posts_not_found(client):
    response = await client.get("/api/users/999/posts")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# UPDATE USER


async def test_update_user(client):
    token = await _create_user_and_token(client)
    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = user_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "updateduser"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


async def test_update_user_not_authorized(client):
    token1 = await _create_user_and_token(client, "user1", "user1@example.com")
    await _create_user_and_token(client, "user2", "user2@example.com")

    user2_response = await client.get("/api/users/2")
    user2_id = user2_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user2_id}",
        headers={"Authorization": f"Bearer {token1}"},
        json={"username": "hacked"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this user"


async def test_update_user_other_user_id_forbidden(client):
    token = await _create_user_and_token(client)

    response = await client.patch(
        "/api/users/999",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "updateduser"},
    )

    assert response.status_code == 403


async def test_update_user_duplicate_username(client):
    await _create_user_and_token(client, "user1", "user1@example.com")
    token2 = await _create_user_and_token(client, "user2", "user2@example.com")

    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token2}"},
    )
    user_id = user_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"username": "user1"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


async def test_update_user_duplicate_email(client):
    await _create_user_and_token(client, "user1", "user1@example.com")
    token2 = await _create_user_and_token(client, "user2", "user2@example.com")

    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token2}"},
    )
    user_id = user_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"email": "user1@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


async def test_update_user_invalid_data(client):
    token = await _create_user_and_token(client)
    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = user_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": ""},
    )

    assert response.status_code == 422


async def test_update_user_email(client):
    token = await _create_user_and_token(client)
    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = user_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"


async def test_update_user_multiple_fields(client):
    token = await _create_user_and_token(client)
    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = user_response.json()["id"]

    response = await client.patch(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "newuser",
            "email": "new@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"


# DELETE USER


async def test_delete_user(client):
    token = await _create_user_and_token(client)
    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = user_response.json()["id"]

    response = await client.delete(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    get_response = await client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404


async def test_delete_user_with_posts(client):
    token = await _create_user_and_token(client, "author", "author@example.com")

    created = await _create_post(client, token, title="Author Post")
    assert created.status_code == 201
    post_id = created.json()["id"]

    user_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = user_response.json()["id"]

    delete_response = await client.delete(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 204

    post_response = await client.get(f"/api/posts/{post_id}")

    # This expectation assumes deleting a user also deletes their posts.
    assert post_response.status_code == 404


async def test_delete_user_not_authorized(client):
    await _create_user_and_token(client, "user1", "user1@example.com")
    token2 = await _create_user_and_token(client, "user2", "user2@example.com")

    user1_response = await client.get("/api/users/1")
    user1_id = user1_response.json()["id"]

    response = await client.delete(
        f"/api/users/{user1_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this user"


async def test_delete_user_other_user_id_forbidden(client):
    token = await _create_user_and_token(client)

    response = await client.delete(
        "/api/users/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
