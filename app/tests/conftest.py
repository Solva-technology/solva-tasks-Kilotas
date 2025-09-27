import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()


# ---------- ENV до импортов приложения ----------
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/postgres")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "postgres")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("BOT_TOKEN", "000000:TEST")
os.environ.setdefault("BOT_SECRET", "super-strong-random-secret")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "")
os.environ.setdefault("REDIS_SSL", "false")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("OVERDUE_SLEEP_SEC", "0")

from app.core import config
config.settings = config.Settings()

from app.main import app



@pytest.fixture
def _patch_overdue_worker(monkeypatch):
    import app.services.overdue_worker as ow

    async def _noop_worker():
        return

    monkeypatch.setattr(ow, "overdue_worker", _noop_worker, raising=True)

@pytest.fixture
def client(_patch_overdue_worker, redis_mock, override_auth, tg_mock):
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()

@pytest.fixture
def redis_mock(monkeypatch):
    class _FakeRedis:
        def __init__(self):
            self.store = {}

        async def set(self, key, value, ex=None, nx=False):
            if nx and key in self.store:
                return False
            self.store[key] = value
            return True

        async def get(self, key):
            return self.store.get(key)

        async def close(self):
            return

    fake = _FakeRedis()
    import app.services.redis_client as rc

    async def _fake_get_redis():
        return fake

    async def _fake_close_redis():
        await fake.close()

    monkeypatch.setattr(rc, "get_redis", _fake_get_redis, raising=True)
    monkeypatch.setattr(rc, "close_redis", _fake_close_redis, raising=True)
    return fake


@pytest.fixture
def override_auth(monkeypatch):
    from datetime import datetime, timezone

    class DummyUser:
        def __init__(
            self,
            id=777,
            role="teacher",
            telegram_id="777",
            username="teacher",
            full_name="Test Teacher",
            email="teacher@example.com",
            is_active=True,
            created_at=None,
            updated_at=None,
        ):
            self.id = id
            self.role = role
            self.telegram_id = telegram_id
            self.username = username
            self.full_name = full_name
            self.email = email
            self.is_active = is_active
            now = datetime.now(timezone.utc)
            self.created_at = created_at or now
            self.updated_at = updated_at or now


    from app.api.routes import groups as groups_module
    app.dependency_overrides[groups_module.require_teacher_or_admin] = lambda: DummyUser(role="teacher")
    if hasattr(groups_module, "get_current_user"):
        app.dependency_overrides[groups_module.get_current_user] = lambda: DummyUser(role="teacher")
    if hasattr(groups_module, "get_current_active_user"):
        app.dependency_overrides[groups_module.get_current_active_user] = lambda: DummyUser(role="teacher")


    try:
        from app.api.routes import auth as auth_module
        if hasattr(auth_module, "get_current_user"):
            app.dependency_overrides[auth_module.get_current_user] = lambda: DummyUser(role="teacher")
        if hasattr(auth_module, "get_current_active_user"):
            app.dependency_overrides[auth_module.get_current_active_user] = lambda: DummyUser(role="teacher")
    except Exception:
        pass

    for mod in ("app.api.auth", "app.deps.auth", "app.core.auth", "app.core.security"):
        try:
            m = __import__(mod, fromlist=["*"])
            fn = getattr(m, "get_current_user", None)
            if fn:
                app.dependency_overrides[fn] = lambda: DummyUser(role="teacher")
            fn2 = getattr(m, "get_current_active_user", None)
            if fn2:
                app.dependency_overrides[fn2] = lambda: DummyUser(role="teacher")
        except Exception:
            pass

    yield
    app.dependency_overrides.clear()




@pytest.fixture
def tg_mock(monkeypatch):
    calls = []

    async def _fake_send(chat_id, text):
        calls.append({"chat_id": str(chat_id), "text": text})

    import app.services.notifier as notifier

    monkeypatch.setattr(notifier, "send_tg_message", _fake_send, raising=True)
    return calls



@pytest.fixture
def client(_patch_overdue_worker, redis_mock, override_auth, tg_mock):
    with TestClient(app) as c:
        yield c

