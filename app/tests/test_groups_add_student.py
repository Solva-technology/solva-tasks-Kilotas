import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token


def test_add_student_to_group_with_teacher():
    with TestClient(app) as client:
        teacher_id = 1
        teacher_token = create_access_token({"sub": str(teacher_id), "role": "teacher"})


        unique_group_name = f"Test Group {uuid.uuid4().hex[:8]}"

        resp_group = client.post(
            "/groups/",
            json={"name": unique_group_name, "manager_id": teacher_id},
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        assert resp_group.status_code == 201, resp_group.text
        group_id = resp_group.json()["id"]

