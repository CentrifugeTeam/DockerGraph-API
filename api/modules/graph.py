from fastapi import APIRouter, WebSocket
from pydantic import field_validator
from sqlalchemy import text

from ..deps import RedisSession, Session
from .containers import ContainerRead


class Graph(ContainerRead):
    edges: list[int] | None

    @field_validator("edges", mode='before')
    @classmethod
    def validate_edges(cls, v: str | None):
        if v is None:
            return v
        return list(map(int, v.split(',')))


r = APIRouter(prefix="/graph")


@r.websocket("/stream")
async def graph(ws: WebSocket, redis: RedisSession):
    await ws.accept()
    last_id = '$'
    while True:
        response = await redis.xread({"graph": last_id}, count=1, block=0)
        _, messages = response[0]
        last_id, payload = messages[0]
        await ws.send_json(payload)


@r.get('', response_model=list[Graph])
async def graph(session: Session):
    sql = text("""SELECT  *,
    (
        SELECT STRING_AGG(CAST(cn2.container_id AS VARCHAR), ',')
        FROM container_network cn1
        JOIN container_network cn2 ON cn1.network_id = cn2.network_id
        WHERE cn1.container_id = c.id AND cn2.container_id != c.id
    ) AS edges
FROM containers c""")
    return (await session.execute(sql)).mappings()
