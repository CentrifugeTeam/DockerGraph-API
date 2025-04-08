from io import BytesIO

import matplotlib.pyplot as plt
import networkx as nx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...deps import Session
from ..graph.manager import graph_manager

r = APIRouter(prefix='/png')


@r.get('', response_class=StreamingResponse)
async def png(session: Session):

    nodes, edges = await graph_manager.get_graph(session)
    graph = nx.Graph()
    for node in nodes:
        graph.add_node(node)
        for net in node.networks:
            graph.subgraph()
    graph.add_nodes_from(
        [node.hostname for node in nodes])
    graph.add_edges_from(
        [(edge.source_host_id, edge.target_host_id) for edge in edges])
    nx.draw(graph)

    # Create a bytes buffer to store the image
    buf = BytesIO()

    # Generate the figure
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='skyblue',
            node_size=800, edge_color='gray')

    # Save the figure to the buffer
    plt.savefig(buf, format="PNG", dpi=300, bbox_inches='tight')
    plt.close()

    # Seek to the beginning of the buffer
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png",
                             headers={
                                 "Content-Disposition": "attachment; filename=graph.png",
                                 "Content-Type": "image/png; charset=utf-8"})
