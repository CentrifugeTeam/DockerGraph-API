from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..db import Container, Host, Network
from .networks.scheme import NetworkRead
from ..deps import Session

r = APIRouter(prefix='/containers')


class ContainerBase(BaseModel):
    name: str
    image: str
    container_id: str
    status: str
    host_id: int
    ip: str
    created_at: datetime


class ContainerCreate(ContainerBase):
    network_ids: list[int]


class ContainerRead(ContainerBase):
    id: int


class ContainersBatchCreate(BaseModel):
    networks: list[NetworkRead]
    containers: list[ContainerCreate]


@r.post('/batch', status_code=status.HTTP_204_NO_CONTENT, responses={
    404: {'detail': 'Object not found', "content": {"application/json": {"example": {'detail': 'Host Not Found'}}}}})
async def batch_create(batch: ContainersBatchCreate, session: Session):
    """Route был сделан как helper для создания нескольких контейнеров с сетями одновременно, нужно записать произвольные значения network.id чтобы сделать ссылку в объекте контейнера на сеть главное чтобы он не повторялся  , в запросе этот network.id меняется."""
    network_lookup = {}
    for network in batch.networks:
        network_db = Network(name=network.name)
        network_lookup[network.id] = network_db

    for container in batch.containers:
        host = await session.get(Host, container.host_id)
        if not host:
            raise HTTPException(status_code=404, detail='Host not found')
        container_db = Container(
            **container.model_dump(exclude={'network_ids', 'host_id'}))
        container_db.host = host

        for network_id in container.network_ids:
            network_db = network_lookup[network_id]
            container_db.networks.append(network_db)

        session.add(container_db)
    await session.commit()

    return


@r.post('', status_code=status.HTTP_204_NO_CONTENT, responses={
    404: {'detail': 'Object not found', "content": {"application/json": {"example": {'detail': 'Host Not Found'}}}}
})
async def containers(containers: list[ContainerCreate], session: Session):
    """Добавление контейнеров на основе сети и хоста"""
    for container in containers:
        host = await session.get(Host, container.host_id)
        if not host:
            raise HTTPException(status_code=404, detail='Host not found')
        container_db = Container(
            **container.model_dump(exclude={'network_ids', 'host_id'}))
        container_db.host = host

        for network_id in container.network_ids:
            network_db = await session.get(Network, network_id)
            if not network_db:
                raise HTTPException(
                    status_code=404, detail='Network not found')
            container_db.networks.append(network_db)
        session.add(container_db)
    await session.commit()

    return
