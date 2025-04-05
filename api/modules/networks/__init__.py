
from fastapi import APIRouter

from ...db import Network
from ...deps import Session
from .scheme import NetworkCreate, NetworkRead

r = APIRouter(prefix='/networks')


@r.post('', response_model=list[NetworkRead])
async def networks(networks: list[NetworkCreate], session: Session):
    """Добавление Docker Networks"""
    response = []
    for network in networks:
        network_db = Network(name=network.name)
        session.add(network_db)
        response.append(network_db)

    await session.commit()
    return response
