from fastapi import APIRouter, WebSocket

from ..deps import RedisSession

r = APIRouter(prefix="/stream")


@r.websocket("/graph")
async def graph(ws: WebSocket, redis: RedisSession):
    await ws.accept()
    last_id = 0
    while True:
        response = await redis.xread({"graph": last_id}, count=1, block=0)
        _, messages = response[0]
        last_id, payload = messages[0]
        await ws.send_json(payload)
