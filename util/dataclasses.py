from dataclasses import dataclass
from .methods import ip_to_int

@dataclass
class Interface:
    name: str
    ip_addr: str
    mac_addr: str
    netmask: str
    gateway: str

    @property
    def prefix_length(self) -> int:
        return bin(ip_to_int(self.netmask)).count('1')

    @property
    def subnet(self) -> str:
        return f'{self.ip_addr}/{self.prefix_length}'

@dataclass
class Host:
    ip_addr: str
    mac_addr: str