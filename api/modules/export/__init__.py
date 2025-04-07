from io import StringIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...deps import Session
from ..graph.manager import graph_manager

r = APIRouter(prefix='/export')


@r.get('/uml', response_class=StreamingResponse)
async def plantuml(session: Session):

    nodes, links = await graph_manager.get_graph(session)
    buffer = StringIO()
    buffer.write("@startuml\n")
    for node in nodes:
        buffer.write(f'object "{node.name}" as {node.id}\n')
    for link in links.values():
        first = link[0]
        for l in link[1:]:
            buffer.write(f'{first} -> {l}\n')
            first = l
    buffer.write("@enduml\n")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="text/plain",
                             headers={
                                 "Content-Disposition": "attachment; filename=graph.puml",
                                 "Content-Type": "text/plain; charset=utf-8"})
