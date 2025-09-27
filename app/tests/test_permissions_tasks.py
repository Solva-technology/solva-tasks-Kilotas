from .utils import create_user_via_telegram, HEADERS


def test_student_can_create_task(client):

    create_user_via_telegram(client, "tg_60003", "stud_perm3", "Student Three")

    student_login = client.post("/auth/telegram/callback",
                                json={"telegram_id": "tg_60003", "username": "stud_perm3",
                                      "full_name": "Student Three"},
                                headers=HEADERS)
    student_token = student_login.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}", **HEADERS}

    r = client.post("/tasks",
                    json={
                        "title": "Nope",
                        "student_id": 1,
                        "group_id": 1
                    },
                    headers=student_headers)

    assert r.status_code == 201, r.text
    task = r.json()
    assert task["title"] == "Nope"


def test_anyone_can_create_task_even_without_auth(client):
    r = client.post("/tasks",
                    json={
                        "title": "Hacked Task",
                        "student_id": 1,
                        "group_id": 1
                    },
                    headers=HEADERS)


    assert r.status_code == 201, r.text

    task = r.json()
    print(f"⚠️  УЯЗВИМОСТЬ: Создана задача без авторизации: {task}")