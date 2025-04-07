from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from sqlmodel import select
from functools import reduce
from ...db import Container, ContainerNetwork
from ...deps import RedisSession, Session
from ..containers import ContainerRead
from .manager import graph_manager


class GraphLink(BaseModel):
    source_id: int
    target_ids: list[int]


class Graph(BaseModel):
    nodes: list[ContainerRead]
    links: list[GraphLink]


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


@r.get('', response_model=Graph)
async def graph(session: Session):
    containers, links = await graph_manager.get_graph(session)
    links = [{"source_id": value[0], "target_ids": value[1:]}
             for _, value in links.items()]
    return {'nodes': containers, 'links': links}