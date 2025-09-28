from fastapi.testclient import TestClient
from app.main import app


def test_teacher_create_task():
    with TestClient(app) as client:
        resp_login = client.post(
            "/auth/telegram/callback",
            json={"telegram_id": "999", "username": "user1", "full_name": "Admin User"},
            headers={"X-Bot-Secret": "super-strong-random-secret"},
        )
        assert resp_login.status_code == 200
        login_data = resp_login.json()
        access_token = login_data["access_token"]

        print("LOGIN RESPONSE:", login_data)
        print("USER ROLE:", login_data.get("role", "unknown"))

        existing_student_id = 2

        existing_group_id = 1

        resp_task = client.post(
            "/tasks/",
            json={
                "title": "Test Task from Admin",
                "description": "Test task description created by admin",
                "student_id": existing_student_id,
                "group_id": existing_group_id,
                "deadline": "2024-12-31T23:59:59",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        print("TASK CREATE STATUS:", resp_task.status_code)
        print("TASK CREATE RESPONSE:", resp_task.text)

        if resp_task.status_code == 403:
            print("❌ У пользователя нет прав на создание задач!")
            print("   Нужна роль teacher или admin")
        else:
            assert resp_task.status_code == 201
            print("✅ Задача успешно создана!")
