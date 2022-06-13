from dataclasses import dataclass

@dataclass
class Interface:
    name: str
    ip_addr: str
    mac_addr: str
    netmask: str
    gateway: str