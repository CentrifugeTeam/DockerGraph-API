from io import StringIO

import networkx as nx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ...db import Network
from ...deps import Session
from ..graph.manager import graph_manager

r = APIRouter(prefix='/export')


def create_mindmap_from_networks(buffer: StringIO, networks: list[Network], start='**'):
    container_start = '*' * (len(start) + 1)
    for network in networks:
        buffer.write(f"{start} {network.name}\n")
        for container in network.containers:
            buffer.write(f"{container_start} {container.name}\n")


@r.get('/plantuml', response_class=StreamingResponse)
async def plantuml(session: Session):

    nodes, edges = await graph_manager.get_graph(session)
    graph = nx.Graph()
    graph.add_nodes_from(
        [(node.id, {'name': node.hostname, "networks": node.networks}) for node in nodes])
    graph.add_edges_from([(edge.source_host_id, edge.target_host_id) for edge in edges])
    buffer = StringIO()
    buffer.write("@startmindmap\ntitle Docker Network\n")
    visited = set()
    for i, node in enumerate(graph.nodes()):
        if node in visited:
            continue
        buffer.write(f"* {graph[node]['name']}\n")
        for neighbor in graph.neighbors(node):
            if neighbor in visited:
                continue
            buffer.write(f"** {graph[neighbor]['name']}\n")
            create_mindmap_from_networks(buffer, graph[neighbor]['networks'], start='***')
            visited.add(neighbor)
        
        create_mindmap_from_networks(buffer, graph[node]['networks'], start='**')
        visited.add(node)
        
        
    buffer.write("@endmindmap\n")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="text/plain",
                             headers={
                                 "Content-Disposition": "attachment; filename=graph.puml",
                                 "Content-Type": "text/plain; charset=utf-8"})
