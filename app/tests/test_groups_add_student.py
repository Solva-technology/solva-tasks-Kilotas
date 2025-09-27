import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token


def test_add_student_to_group_with_teacher():
    with TestClient(app) as client:
        # 1. создаём учителя
        resp_user = client.post(
            "/users/",
            json={
                "telegram_id": f"tg_teacher_{uuid.uuid4().hex[:6]}",
                "username": "teacher_test",
                "full_name": "Teacher Test",
                "role": "teacher",
            },
        )
        assert resp_user.status_code == 201, resp_user.text
        teacher = resp_user.json()
        teacher_id = teacher["id"]


        teacher_token = create_access_token({"sub": str(teacher_id), "role": "teacher"})


        unique_group_name = f"Test Group {uuid.uuid4().hex[:8]}"
        resp_group = client.post(
            "/groups/",
            json={"name": unique_group_name, "manager_id": teacher_id},
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert resp_group.status_code == 201, resp_group.text
        group_id = resp_group.json()["id"]


        resp_student = client.post(
            "/users/",
            json={
                "telegram_id": f"tg_student_{uuid.uuid4().hex[:6]}",
                "username": "student_test",
                "full_name": "Student Test",
                "role": "student",
            },
        )
        assert resp_student.status_code == 201, resp_student.text
        student = resp_student.json()
        student_id = student["id"]


        resp_add = client.post(
            f"/groups/{group_id}/students",
            json={"student_id": student_id},
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert resp_add.status_code == 200, resp_add.text

