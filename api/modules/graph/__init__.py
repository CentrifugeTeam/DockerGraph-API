import asyncio
import random
from functools import reduce
from uuid import UUID

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ...db import Container, Host, HostToHost, Network
from ...deps import RedisSession, Session
from ..containers import ContainerBase, ContainerReadV2
from ..hosts.scheme import HostRead
from ..networks import NetworkRead
from ..networks import manager as network_manager
from .manager import graph_manager


class NetworkLink(BaseModel):
    source_id: UUID
    target_id: UUID


class GraphNetworkRead(NetworkRead):
    containers: list[ContainerReadV2]


class GraphHostRead(HostRead):
    networks: list[GraphNetworkRead]


class Graph(BaseModel):
    nodes: list[GraphHostRead]
    links: list[NetworkLink]

    @field_validator('links', mode='before')
    @classmethod
    def validate(cls, links: list[HostToHost]):
        for link in links:
            yield {'source_id': link.source_host_id, 'target_id': link.target_host_id}


r = APIRouter(prefix="/graph")


class Proxy:

    def __init__(self, proxied, hosts):
        self.proxied = proxied
        self.hosts = hosts

    def __getattr__(self, name):
        return getattr(self.proxied, name)


@r.websocket("/stream")
async def graph(ws: WebSocket, redis: RedisSession, session: Session):
    await ws.accept()
    # last_id = '$'
    networks = (await session.exec(select(Network).options(joinedload(Network.containers)))).unique().all()

    while True:
        await asyncio.sleep(0.5)
        network = random.choice(networks)
        mock = []
        packets = 0
        for i in range(random.randint(1, 10)):
            packet = random.randint(10, 100)
            mock.append({**random.choice(network.containers).model_dump(
                exclude={'last_active', 'created_at', 'packets_number'}), 'packets_number': packet, "traffic": {}})
            packets += packet

        # response = await redis.xread({"graph": last_id}, count=1, block=0)
        # _, messages = response[0]
        # last_id, payload = messages[0]
        await ws.send_json({'network': {'id': network.id, 'packets': packets, 'containers': mock}})


@r.get('', response_model=Graph)
async def graph(session: Session, host_id: UUID | None = None):
    if host_id:
        nodes = (await session.exec(select(Host).where(Host.id == host_id).options(joinedload(Host.networks).subqueryload(Network.containers)))).unique()
        links = []
    else:
        nodes = (await session.exec(select(Host).options(joinedload(Host.networks).subqueryload(Network.containers)))).unique()
        links = (await session.exec(select(HostToHost)))
    return {'nodes': nodes, 'links': links}
