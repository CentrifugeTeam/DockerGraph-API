from fastapi import FastAPI

from .modules import stream

app = FastAPI()
app.include_router(stream.r)
