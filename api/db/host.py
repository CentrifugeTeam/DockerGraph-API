from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from .mixins import IDMixin




class Host(IDMixin, SQLModel, table=True):
    __tablename__ = "hosts"
    hostname: str
    ip: str
    agent_id: UUID = Field(default_factory=uuid4)
    token: str
    containers: list['Container'] = Relationship(back_populates="host")


class ContainerNetwork(SQLModel, table=True):
    __tablename__ = "container_network"
    network_id: int = Field(foreign_key="networks.id", primary_key=True)
    container_id: int = Field(foreign_key="containers.id", primary_key=True)
    __table_args__ = (UniqueConstraint("network_id", "container_id"),)


class Network(IDMixin, SQLModel, table=True):
    __tablename__ = "networks"
    name: str
    network_id: str
    containers: list['Container'] = Relationship(
        back_populates='networks', link_model=ContainerNetwork)


class Container(IDMixin, SQLModel, table=True):
    __tablename__ = "containers"
    name: str
    container_id: str
    image: str
    status: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False))
    host_id: int = Field(foreign_key="hosts.id")
    ip: str
    host: Host = Relationship(back_populates="containers")
    networks: list[Network] = Relationship(
        back_populates="containers", link_model=ContainerNetwork)
