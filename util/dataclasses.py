from dataclasses import dataclass

@dataclass
class Interface:
    id: str
    ip_addr: str
    mac_addr: str
    gateway: str
    netmask: str