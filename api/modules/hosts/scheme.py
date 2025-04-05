from pydantic import BaseModel


class HostCreate(BaseModel):
    hostname: str
    ip: str


class HostRead(HostCreate):
    id: int