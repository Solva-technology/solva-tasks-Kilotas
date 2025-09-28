import os

HEADERS = {"X-Bot-Secret": os.getenv("BOT_SECRET", "super-strong-random-secret")}


def create_user_via_telegram(client, telegram_id: str, username: str, full_name: str):
    r = client.post(
        "/auth/telegram/callback",
        json={"telegram_id": telegram_id, "username": username, "full_name": full_name},
        headers=HEADERS,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    token = data.get("access_token")
    assert token, "callback must return access_token"

    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    me_data = me.json()
    data["user_id"] = me_data.get("id") or me_data.get("user_id")
    assert data["user_id"], "users/me must return id"
