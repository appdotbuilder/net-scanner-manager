from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)
class Network(SQLModel, table=True):
    __tablename__ = "networks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    subnet: str = Field(max_length=18)  # e.g., "192.168.1.0/24"
    gateway_ip: str = Field(max_length=15)
    description: str = Field(default="", max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    devices: List["Device"] = Relationship(back_populates="network")
    scans: List["NetworkScan"] = Relationship(back_populates="network")


class Device(SQLModel, table=True):
    __tablename__ = "devices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(max_length=15, index=True)
    mac_address: str = Field(default="", max_length=17)
    hostname: str = Field(default="", max_length=255)
    device_type: str = Field(default="unknown", max_length=50)  # router, computer, mobile, etc.
    manufacturer: str = Field(default="", max_length=100)
    operating_system: str = Field(default="", max_length=100)
    is_online: bool = Field(default=True)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    network_id: int = Field(foreign_key="networks.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    network: Network = Relationship(back_populates="devices")
    ports: List["Port"] = Relationship(back_populates="device")


class IPAddress(SQLModel, table=True):
    __tablename__ = "ip_addresses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(max_length=15, unique=True, index=True)
    country: str = Field(default="", max_length=100)
    country_code: str = Field(default="", max_length=2)
    city: str = Field(default="", max_length=100)
    region: str = Field(default="", max_length=100)
    latitude: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=8)
    longitude: Optional[Decimal] = Field(default=None, max_digits=11, decimal_places=8)
    isp: str = Field(default="", max_length=200)
    organization: str = Field(default="", max_length=200)
    is_monitored: bool = Field(default=True)
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    ports: List["Port"] = Relationship(back_populates="ip_address")


class Port(SQLModel, table=True):
    __tablename__ = "ports"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    port_number: int = Field(ge=1, le=65535)
    protocol: str = Field(max_length=10, default="tcp")  # tcp, udp
    state: str = Field(max_length=20, default="open")  # open, closed, filtered
    service: str = Field(default="", max_length=100)  # http, ssh, ftp, etc.
    version: str = Field(default="", max_length=200)
    banner: str = Field(default="", max_length=500)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    ip_address_id: Optional[int] = Field(default=None, foreign_key="ip_addresses.id")
    last_scanned: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    device: Optional[Device] = Relationship(back_populates="ports")
    ip_address: Optional[IPAddress] = Relationship(back_populates="ports")


class NetworkScan(SQLModel, table=True):
    __tablename__ = "network_scans"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    network_id: int = Field(foreign_key="networks.id")
    scan_type: str = Field(max_length=50, default="ping_sweep")  # ping_sweep, port_scan, full_scan
    status: str = Field(max_length=20, default="pending")  # pending, running, completed, failed
    devices_found: int = Field(default=0, ge=0)
    ports_found: int = Field(default=0, ge=0)
    scan_duration: Optional[int] = Field(default=None, ge=0)  # seconds
    scan_options: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    error_message: str = Field(default="", max_length=1000)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    network: Network = Relationship(back_populates="scans")


# Non-persistent schemas (for validation, forms, API requests/responses)
class NetworkCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    subnet: str = Field(max_length=18)
    gateway_ip: str = Field(max_length=15)
    description: str = Field(default="", max_length=500)


class NetworkUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    subnet: Optional[str] = Field(default=None, max_length=18)
    gateway_ip: Optional[str] = Field(default=None, max_length=15)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)


class DeviceCreate(SQLModel, table=False):
    ip_address: str = Field(max_length=15)
    mac_address: str = Field(default="", max_length=17)
    hostname: str = Field(default="", max_length=255)
    device_type: str = Field(default="unknown", max_length=50)
    network_id: int


class DeviceUpdate(SQLModel, table=False):
    hostname: Optional[str] = Field(default=None, max_length=255)
    device_type: Optional[str] = Field(default=None, max_length=50)
    manufacturer: Optional[str] = Field(default=None, max_length=100)
    operating_system: Optional[str] = Field(default=None, max_length=100)
    is_online: Optional[bool] = Field(default=None)


class IPAddressCreate(SQLModel, table=False):
    ip_address: str = Field(max_length=15)
    notes: str = Field(default="", max_length=1000)


class IPAddressUpdate(SQLModel, table=False):
    country: Optional[str] = Field(default=None, max_length=100)
    country_code: Optional[str] = Field(default=None, max_length=2)
    city: Optional[str] = Field(default=None, max_length=100)
    region: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=8)
    longitude: Optional[Decimal] = Field(default=None, max_digits=11, decimal_places=8)
    isp: Optional[str] = Field(default=None, max_length=200)
    organization: Optional[str] = Field(default=None, max_length=200)
    is_monitored: Optional[bool] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=1000)


class PortCreate(SQLModel, table=False):
    port_number: int = Field(ge=1, le=65535)
    protocol: str = Field(max_length=10, default="tcp")
    device_id: Optional[int] = Field(default=None)
    ip_address_id: Optional[int] = Field(default=None)


class NetworkScanCreate(SQLModel, table=False):
    network_id: int
    scan_type: str = Field(max_length=50, default="ping_sweep")
    scan_options: Dict[str, Any] = Field(default={})


class NetworkScanUpdate(SQLModel, table=False):
    status: Optional[str] = Field(default=None, max_length=20)
    devices_found: Optional[int] = Field(default=None, ge=0)
    ports_found: Optional[int] = Field(default=None, ge=0)
    scan_duration: Optional[int] = Field(default=None, ge=0)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    completed_at: Optional[datetime] = Field(default=None)
