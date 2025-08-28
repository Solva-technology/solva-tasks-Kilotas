from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from sqlalchemy import text

from app.core.logging import setup_logging
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.routes import auth as auth_router
from app.api.routes import users as users_router
from app.api.routes import groups as groups_router


setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info({"action": "service_start"})
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text("SELECT 1"))
        yield
    finally:
        await engine.dispose()
        log.info({"action": "service_stop"})


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "status": "ok"}


app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(groups_router.router)




