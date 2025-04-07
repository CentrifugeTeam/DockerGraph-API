from fastapi import FastAPI

from .modules import auth, containers, graph, networks
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph.r)
app.include_router(containers.r)
app.include_router(auth.r)
app.include_router(networks.r)
