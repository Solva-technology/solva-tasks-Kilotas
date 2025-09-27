import uuid
import base64
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def decode_sub_from_token(token: str) -> int:
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return int(json.loads(base64.urlsafe_b64decode(payload).decode())["sub"])


def test_add_student_to_group_with_teacher():
    with TestClient(app) as client:
        resp_teacher = client.post(
            "/auth/telegram/callback",
            json={
                "telegram_id": f"tg_teacher_{uuid.uuid4().hex[:6]}",
                "username": "teacher_test",
                "full_name": "Teacher Test",
            },
            headers={"X-Bot-Secret": getattr(settings, "BOT_SECRET", "my-bot-secret")},
        )
        assert resp_teacher.status_code == 200, resp_teacher.text
        teacher_token = resp_teacher.json()["access_token"]
        teacher_id = decode_sub_from_token(teacher_token)


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
            headers={"X-Bot-Secret": getattr(settings, "BOT_SECRET", "my-bot-secret")},
        )
        assert resp_student.status_code == 200, resp_student.text
        student_token = resp_student.json()["access_token"]
        student_id = decode_sub_from_token(student_token)


        resp_add = client.post(
            f"/groups/{group_id}/students",
            json={"student_id": student_id},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert resp_add.status_code == 200, resp_add.text
