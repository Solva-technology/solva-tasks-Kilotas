import asyncio
import contextlib
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from sqlalchemy import text

from app.admin.panel import init_admin
from app.core.logging import setup_logging
from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.api.routes import auth as auth_router
from app.api.routes import users as users_router
from app.api.routes import groups as groups_router
from app.api.routes import tasks as tasks_router
from app.api.routes import debug as debug_router
from app.services.overdue_worker import overdue_worker
from app.services.redis_client import close_redis

setup_logging()
log = logging.getLogger(__name__)


async def init_defaults():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(text("SELECT 1"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info({"action": "service_start"})
    worker_task = None
    if not settings.TESTING:
        worker_task = asyncio.create_task(overdue_worker())
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await init_defaults()
        yield
    finally:
        if worker_task:
            worker_task.cancel()
            with contextlib.suppress(Exception):
                await worker_task
        await engine.dispose()
        await close_redis()
        log.info({"action": "service_stop"})


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

logging.getLogger(__name__).warning("BOT_TOKEN loaded in API: %s", bool(settings.BOT_TOKEN))

admin = init_admin(app)


@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "status": "ok"}


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(groups_router.router)
app.include_router(tasks_router.router)
app.include_router(debug_router.router)




