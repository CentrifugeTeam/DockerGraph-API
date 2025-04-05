from fastapi import APIRouter, WebSocket
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ..db import Container
from ..deps import RedisSession, Session

r = APIRouter(prefix="/graph")


@r.websocket("/stream")
async def graph(ws: WebSocket, redis: RedisSession):
    await ws.accept()
    last_id = 0
    while True:
        response = await redis.xread({"graph": last_id}, count=1, block=0)
        _, messages = response[0]
        last_id, payload = messages[0]
        await ws.send_json(payload)


# @r.get('', response_model=list[Graph])
async def graph(session: Session):
    # TODO
    sql = """WITH RECURSIVE graph AS (
        SELECT * FROM containers
        
        UNION ALL
        
        SELECT * FROM container_links
        
            
    )
    
    """
    return (await session.exec(select(Container).options(joinedload(Container.containers)))).unique().all()
