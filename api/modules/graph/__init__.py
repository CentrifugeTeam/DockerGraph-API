from functools import reduce

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ...db import Cluster, ClusterHost, Container, Host, Network
from ...deps import RedisSession, Session
from ..containers import ContainerBase, ContainerReadV2
from ..hosts.scheme import HostRead
from ..networks import NetworkRead
from .manager import graph_manager


class NetworkLink(BaseModel):
    source_id: int
    target_ids: int


class GraphNetworkRead(NetworkRead):
    containers: list[ContainerReadV2]


class GraphInnerHostRead(HostRead):
    networks: list[GraphNetworkRead]


class GraphHostRead(HostRead):
    networks: list[GraphNetworkRead]
    hosts: list[GraphInnerHostRead] = None


class Graph(BaseModel):
    hosts: list[GraphHostRead]
    network_links: list[NetworkLink]


r = APIRouter(prefix="/graph")


class Proxy:

    def __init__(self, proxied, hosts):
        self.proxied = proxied
        self.hosts = hosts

    def __getattr__(self, name):
        return getattr(self.proxied, name)


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
    clusters = (await session.exec(select(Cluster).options(joinedload(Cluster.hosts).subqueryload(Host.networks).subqueryload(Network.containers)))).unique()
    hosts = []
    hosts_ids = []
    for cluster in clusters:
        for host in cluster.hosts:
            hosts_ids.append(host.id)
        hosts.append(Proxy(cluster.hosts[0], cluster.hosts[1:]))

    solo_hosts = (await session.exec(select(Host).where(Host.id.not_in(hosts_ids)).options(joinedload(Host.networks).subqueryload(Network.containers)))).unique().all()
    hosts.extend(solo_hosts)
    return {'hosts': hosts, 'network_links': []}
