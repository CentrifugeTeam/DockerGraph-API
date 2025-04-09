from datetime import datetime, timedelta, timezone
from functools import reduce
from uuid import UUID

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ...db import Container, Host, HostToHost, Network, NetworkToNetwork
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


class NetworkToNetworkRead(BaseModel):
    source_id: int
    target_id: int


class Graph(BaseModel):
    nodes: list[GraphHostRead]
    links: list[NetworkLink]
    network_to_network: list[NetworkToNetworkRead]

    @field_validator("links", mode="before")
    @classmethod
    def validate(cls, links: list[HostToHost]):
        for link in links:
            yield {"source_id": link.source_host_id, "target_id": link.target_host_id}

    @field_validator("network_to_network", mode="before")
    @classmethod
    def validate_ntn(cls, nets: list[NetworkToNetwork]):
        for net in nets:
            yield {"source_id": net.source_network_id, "target_id": net.target_network_id}


r = APIRouter(prefix="/graph", tags=["Graph"])


class Proxy:
    def __init__(self, proxied, hosts):
        self.proxied = proxied
        self.hosts = hosts

    def __getattr__(self, name):
        return getattr(self.proxied, name)


@r.get("", response_model=Graph)
async def graph(session: Session, host_id: UUID | None = None, is_dead: bool | None = None):
    nodes, links, net_to_net = await graph_manager.get_full_graph(session, host_id, is_dead)
    return {"nodes": nodes, "links": links, "network_to_network": net_to_net}
