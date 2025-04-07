from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from sqlmodel import select
from functools import reduce
from ..db import Container, ContainerNetwork
from ..deps import RedisSession, Session
from .containers import ContainerRead


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
    containers = await session.exec(select(Container))
    container_networks = await session.exec(select(ContainerNetwork))
    links = {}
    for network in container_networks:
        if network.network_id not in links:
            links[network.network_id] = {network.container_id}
        else:
            links[network.network_id].add(network.container_id)
    res_links = []
    for link in links:
        outputs = set()
        reduce(lambda x, y: x.union(y), links[link], outputs)
        for link2 in links:
            outputs = outputs.union(link2)
        outputs = list(outputs)
        source_id, target_ids = outputs[0], outputs[1:]
        res_links.append({"source_id": source_id, "target_ids": target_ids})
        
    return {'nodes': containers, 'links': res_links}
