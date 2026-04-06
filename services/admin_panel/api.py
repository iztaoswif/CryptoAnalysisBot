from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from redis.asyncio import Redis
from app_data.redis import get_redis

admin_panel_app = FastAPI()


@admin_panel_app.middleware("http")
async def restrict_to_localhost(request: Request, call_next):
    if request.client is None or request.client.host not in ["127.0.0.1", "localhost"]:
        raise HTTPException(status_code=404, detail="Not found")
    return await call_next(request)


class ChangeRequest(BaseModel):
    window_ms: Optional[int] = None
    spike_threshold: Optional[float] = None


@admin_panel_app.patch("/change")
async def change_parameters(
    config: ChangeRequest,
    redis_client: Redis = Depends(get_redis)):

    if config.window_ms is not None:
        await redis_client.set("window_ms", config.window_ms)

    if config.spike_threshold is not None:
        await redis_client.set("spike_threshold", config.spike_threshold)

    return {"status": "updated"}
