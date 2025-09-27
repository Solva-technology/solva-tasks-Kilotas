import uuid
from fastapi.testclient import TestClient
from app.main import app

def test_add_student_to_group_with_teacher():
    with TestClient(app) as client:
        resp_teacher = client.post(
            "/auth/telegram/callback",
            json={
                "telegram_id": f"tg_teacher_{uuid.uuid4().hex[:6]}",
                "username": "teacher_test",
                "full_name": "Teacher Test",
            },
            headers={"X-Bot-Secret": "my-bot-secret"},
        )
        assert resp_teacher.status_code == 200, resp_teacher.text
        teacher_data = resp_teacher.json()
        teacher_token = teacher_data["access_token"]
        teacher_id = teacher_data["id"]

        unique_group_name = f"Test Group {uuid.uuid4().hex[:8]}"
        resp_group = client.post(
            "/groups/",
            json={"name": unique_group_name, "manager_id": teacher_id},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert resp_group.status_code == 201, resp_group.text
        group_id = resp_group.json()["id"]

        # создаём студента
        resp_student = client.post(
            "/auth/telegram/callback",
            json={
                "telegram_id": f"tg_student_{uuid.uuid4().hex[:6]}",
                "username": "student_test",
                "full_name": "Student Test",
            },
            headers={"X-Bot-Secret": "my-bot-secret"},
        )
        assert resp_student.status_code == 200, resp_student.text
        student_data = resp_student.json()
        student_id = student_data["id"]


        resp_add = client.post(
            f"/groups/{group_id}/add_student",
            params={"student_id": student_id},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert resp_add.status_code == 200, resp_add.text
        data = resp_add.json()
        assert student_id in data["students"]
