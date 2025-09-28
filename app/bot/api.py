import httpx

BACKEND_URL = "http://127.0.0.1:8000"


async def api_post(
    path: str,
    *,
    json: dict | None = None,
    token: str | None = None,
    headers: dict | None = None,
):
    async with httpx.AsyncClient(timeout=10) as client:
        hdrs = {"Content-Type": "application/json", **(headers or {})}
        if token:
            hdrs["Authorization"] = f"Bearer {token}"
        return await client.post(f"{BACKEND_URL}{path}", json=json, headers=hdrs)


async def api_get(path: str, *, token: str, params: dict | None = None):
    async with httpx.AsyncClient(timeout=10) as client:
        return await client.get(
            f"{BACKEND_URL}{path}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )


async def api_patch(path: str, *, json: dict | None = None, token: str | None = None):
    print(f"🔍 PATCH {path} with JSON: {json}")
    async with httpx.AsyncClient(timeout=10) as client:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return await client.patch(f"{BACKEND_URL}{path}", json=json, headers=headers)
