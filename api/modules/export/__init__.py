from io import StringIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...deps import Session
from ..graph.manager import graph_manager

r = APIRouter(prefix='/export')


@r.get('/plantuml', response_class=StreamingResponse)
async def plantuml(session: Session):

    nodes, links = await graph_manager.get_graph(session)
    buffer = StringIO()
    buffer.write("@startmindmap\ntitle Docker Network\n")
    hashmap = {node.id: node for node in nodes}
    for link in links.values():
        for i, l in enumerate(link):
            buffer.write(f"{(i+1) * '*'} {hashmap[l].name}\n")
    buffer.write("@endmindmap\n")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="text/plain",
                             headers={
                                 "Content-Disposition": "attachment; filename=graph.puml",
                                 "Content-Type": "text/plain; charset=utf-8"})
