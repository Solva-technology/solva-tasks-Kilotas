import pytest
from httpx import AsyncClient
from app.db.models.user import UserRole


@pytest.mark.asyncio
async def test_add_student_to_group_with_teacher(async_client: AsyncClient, create_user, create_group):
    teacher = await create_user(role=UserRole.teacher)
    student = await create_user(role=UserRole.student)

    async_client.headers.update({"Authorization": f"Bearer {teacher.token}"})

    group = await create_group(manager_id=teacher.id)

    resp = await async_client.post(
        f"/groups/{group.id}/add_student",
        params={"student_id": student.id}
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert student.id in data["students"]


@pytest.mark.asyncio
async def test_student_can_create_task(async_client: AsyncClient, create_user, create_group):
    student = await create_user(role=UserRole.student)
    async_client.headers.update({"Authorization": f"Bearer {student.token}"})

    group = await create_group(manager_id=student.id)

    resp = await async_client.post(
        "/tasks/",
        json={
            "title": "Task 1",
            "description": "Test",
            "group_id": group.id,
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Task 1"


@pytest.mark.asyncio
async def test_anyone_can_create_task_even_without_auth(async_client: AsyncClient, create_group):
    group = await create_group()

    resp = await async_client.post(
        "/tasks/",
        json={
            "title": "Anon Task",
            "description": "From anon",
            "group_id": group.id,
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Anon Task"
