from .utils import create_user_via_telegram, HEADERS


def test_student_updates_task_status(client):

    create_user_via_telegram(
        client=client,
        telegram_id="tg_40901",
        username="teacher_user",
        full_name="Teacher Name"
    )

    create_user_via_telegram(
        client=client,
        telegram_id="tg_40902",
        username="student_user",
        full_name="Student Name"
    )


    teacher_login = client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "tg_40901",
            "username": "teacher_user",
            "full_name": "Teacher Name"
        },
        headers=HEADERS
    )

    teacher_token = teacher_login.json()["access_token"]

    student_login = client.post(
        "/auth/telegram/callback",
        json={
            "telegram_id": "tg_40902",
            "username": "student_user",
            "full_name": "Student Name"
        },
        headers=HEADERS
    )
    student_token = student_login.json()["access_token"]


    teacher_headers = {"Authorization": f"Bearer {teacher_token}", **HEADERS}
    student_headers = {"Authorization": f"Bearer {student_token}", **HEADERS}

