from pydantic import BaseModel


class NetworkCreate(BaseModel):
    name: str
    network_id: str
    display_name: str | None = None


class NetworkRead(NetworkCreate):
    id: int


class OverlayNetworkCreate(NetworkCreate):
    peers: list[str]
