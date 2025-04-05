from fastapi import FastAPI

from .modules import auth, containers, graph, networks

app = FastAPI()
app.include_router(graph.r)
app.include_router(containers.r)
app.include_router(auth.r)
app.include_router(networks.r)
