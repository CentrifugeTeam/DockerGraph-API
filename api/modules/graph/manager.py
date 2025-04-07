from sqlmodel import select

from ...db import Container, Network
from ...deps import Session


class GraphManager:

    async def get_graph(self, session: Session, options=()):
        nodes = await session.exec(select(Container).options(*options))
        container_networks = await session.exec(select(Network))
        links = {}
        for network in container_networks:
            if network.network_id not in links:
                links[network.network_id] = [network.container_id]
            else:
                links[network.network_id].append(network.container_id)
        return nodes, links


graph_manager = GraphManager()
