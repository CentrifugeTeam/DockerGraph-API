from uuid import UUID
from sqlalchemy.orm import joinedload
from sqlmodel import select

from ...db import Host, HostToHost, Network, Container, NetworkToNetwork
from datetime import datetime, timezone, timedelta
from ...deps import Session


class GraphManager:

    async def get_graph(self, session: Session, options=()):
        nodes = (await session.exec(select(Host).options(joinedload(Host.networks).subqueryload(Network.containers)))).unique()
        edges = (await session.exec(select(HostToHost)))
        return nodes, edges
    
    async def get_graph_by_id(self, session: Session, id: UUID):
        return (await session.exec(select(Host).where(Host.id == id).options(joinedload(Host.networks).subqueryload(Network.containers)))).unique(), []
    
    async def get_full_graph(self, session, host_id: UUID | None = None, is_dead: bool | None = None):
        if host_id:
            stmt = select(Host).where(Host.id == host_id)
            if is_dead:
                stmt = stmt.join(Network, Network.host_id == Host.id).join(
                    Container, Container.network_id == Network.id)
                nodes = (await session.exec(stmt.options(joinedload(Host.networks).subqueryload(Network.containers)))).unique().all()
                if nodes:
                    for net in nodes[0].networks:
                        containers = [container for container in net.containers if container.last_active < datetime.now(
                            tz=timezone.utc) - timedelta(days=1)]
                        net.containers = containers
            else:
                nodes = (await session.exec(stmt.options(joinedload(Host.networks).subqueryload(Network.containers)))).unique()
            links = []
            net_to_net = []
        else:
            if is_dead:
                stmt = select(Host).join(Network, Network.host_id == Host.id).join(
                    Container, Container.network_id == Network.id)
                nodes = (await session.exec(stmt.options(joinedload(Host.networks).subqueryload(Network.containers)))).unique().all()
                node_ids = []
                networks_ids = []
                for host in nodes:
                    node_ids.append(host.id)
                    for net in host.networks:
                        containers = [container for container in net.containers if container.last_active < datetime.now(
                            tz=timezone.utc) - timedelta(days=1)]
                        net.containers = containers
                        networks_ids.append(net.id)
                with session.no_autoflush:
                    links = await session.exec(select(HostToHost).where((HostToHost.source_host_id.in_(node_ids)) & (HostToHost.target_host_id.in_(node_ids))))
                    net_to_net = await session.exec(select(NetworkToNetwork).where(NetworkToNetwork.source_network_id.in_(networks_ids), NetworkToNetwork.target_network_id.in_(networks_ids)))
                # TODO mock for now

            else:
                nodes = (await session.exec(select(Host).options(joinedload(Host.networks).subqueryload(Network.containers)))).unique()
                links = (await session.exec(select(HostToHost)))
                net_to_net = await session.exec(select(NetworkToNetwork))
                
        return nodes, links, net_to_net


graph_manager = GraphManager()
