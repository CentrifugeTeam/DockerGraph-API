from contextlib import suppress

from sqlalchemy.orm import joinedload
from sqlmodel import select

from ...auth import AuthAPIRouter
from ...db import Network, NetworkHost
from ...deps import Agent, Session
from .scheme import NetworkCreate, NetworkRead

r = AuthAPIRouter(prefix="/networks")


@r.post("", response_model=list[NetworkRead])
async def networks(networks: list[NetworkCreate], session: Session, agent: Agent):
    """Добавление Docker Networks"""
    response = []
    for network in networks:
        stmt = (
            select(Network)
            .where(Network.network_id == network.network_id)
        )
        result = (await session.exec(stmt)).all()
        if result:
            network_db = result[0]
        if not result:
            network_db = Network(**network.model_dump())
            network_db.hosts.append(agent)
            session.add(network_db)
        else:
            query = await session.exec(select(NetworkHost).where(NetworkHost.network_id == network_db.id, NetworkHost.host_id == agent.id))
            if not query.one_or_none():
                session.add(NetworkHost(network_id=network_db.id, host_id=agent.id))

        response.append(network_db)

    await session.commit()
    return response
