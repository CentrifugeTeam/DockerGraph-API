import asyncio
import random
from contextlib import asynccontextmanager
from logging import getLogger

from sqlalchemy.orm import joinedload
from sqlmodel import select

from .db import Network
from .modules.graph.manager import graph_manager
from .deps import get_session

log = getLogger(__name__)
_session = asynccontextmanager(get_session)


async def agent():
    while True:
        try:
            async with _session() as session:
                await graph_manager.get_full_graph(session)
                networks = (await session.exec(select(Network).options(joinedload(Network.containers)))).unique().all()

                for network in networks:
                    network_packets = 0
                    for container in network.containers:
                        container_packet = random.randint(0, 100)
                        container.packets_number = container_packet
                        network_packets += container_packet
                        session.add(container)

                    network.packets_number = network_packets
                    session.add(network)

                await session.commit()
            await asyncio.sleep(300)
        except Exception as e:
            log.exception(exc_info=e)
