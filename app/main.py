from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import init_db
from app.api.routes import translate

from fastapi_limiter import FastAPILimiter

import redis.asyncio as redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    init_db()
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.redis.aclose()


app = FastAPI(title="Video Translation Server", lifespan=lifespan)

app.include_router(translate.router)
