from pydantic import BaseModel
from fastapi_sqlalchemy_toolkit import make_partial_model


class NetworkCreate(BaseModel):
    name: str
    network_id: str
    display_name: str | None = None


class NetworkRead(NetworkCreate):
    id: int


class OverlayNetworkCreate(NetworkCreate):
    peers: list[str]


class NetworkUpdate(BaseModel):
    display_name: str | None = None