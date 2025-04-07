from fastapi.responses import StreamingResponse
from fastapi_sqlalchemy_toolkit import ModelManager, make_partial_model
from pydantic import BaseModel
from ..auth import AuthAPIRouter
from ..graph.manager import graph_manager
import  networkx  as nx
from io import BytesIO
from ...deps import Session

r = AuthAPIRouter(prefix='/export')


async def create_plantuml(nodes, links):
    pass

@r.get('/uml')
async def plantuml(session: Session):
    nodes, links = await graph_manager.get_graph(session)
    
    return StreamingResponse(create_plantuml(nodes, links), media_type="text/plain")    
