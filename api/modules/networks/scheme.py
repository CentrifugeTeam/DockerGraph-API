from pydantic import BaseModel


class NetworkCreate(BaseModel):
    name: str


class NetworkRead(NetworkCreate):
    id: int
