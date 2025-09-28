from fastapi.testclient import TestClient
from app.main import app


def test_telegram_callback_existing_user():
    with TestClient(app) as client:
        telegram_data = {
            "telegram_id": "987654321",
            "username": "existing_user",
            "full_name": "Existing User",
        }

        client.post(
            "/auth/telegram/callback",
            json=telegram_data,
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )

        response = client.post(
            "/auth/telegram/callback",
            json=telegram_data,
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )

        assert response.status_code == 200
        assert "access_token" in response.json()


def test_telegram_callback_invalid_secret():
    with TestClient(app) as client:
        response = client.post(
            "/auth/telegram/callback",
            json={
                "telegram_id": "123",
                "username": "test",
                "full_name": "Test User",
            },
            headers={"X-Bot-Secret": "wrong-secret"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "invalid bot secret"


def test_telegram_callback_update_user_info():
    with TestClient(app) as client:
        create_data = {
            "telegram_id": "555555555",
            "username": "old_username",
            "full_name": "Old Name",
        }

        client.post(
            "/auth/telegram/callback",
            json=create_data,
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )

        update_data = {
            "telegram_id": "555555555",
            "username": "new_username",
            "full_name": "New Name",
        }

        response = client.post(
            "/auth/telegram/callback",
            json=update_data,
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )

        assert response.status_code == 200


def test_telegram_callback_missing_fields():
    with TestClient(app) as client:
        response = client.post(
            "/auth/telegram/callback",
            json={
                "username": "test_user",
                "full_name": "Test User",
            },
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )

        assert response.status_code == 422


def test_user_role_assignment():
    with TestClient(app) as client:
        response = client.post(
            "/auth/telegram/callback",
            json={
                "telegram_id": "999999999",
                "username": "test_student",
                "full_name": "Test Student",
            },
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )

        data = response.json()
        assert data["role"] == "student"
