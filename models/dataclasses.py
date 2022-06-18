from dataclasses import dataclass
from functools import reduce

@dataclass
class Interface:
    name: str
    ip_addr: str
    mac_addr: str
    netmask: str
    gateway: str

    @property
    def prefix_length(self) -> int:
        return bin(
            # Converts self.ip_addr to an integer
            reduce(lambda r, e: r*2**8 + int(e), self.ip_addr.split('.'), 0)
        ).count('1')

    @property
    def subnet(self) -> str:
        return f'{self.ip_addr}/{self.prefix_length}'

@dataclass
class Host:
    ip_addr: str
    mac_addr: str

@dataclass
class ARPAttackSettings:
    interface: Interface
    sources: list[Host]
    destinations: list[Host]
    two_way: bool
    initial_packets: int
    seconds_interval: int

    @property
    def me(self):
        return Host(
            self.interface.ip_addr,
            self.interface.mac_addr
        )

@dataclass
class DNSEntry:
    url: str
    type: str
    ip: str

@dataclass
class DNSAttackSettings:
    arp_settings: ARPAttackSettings
    dns_rules: list[DNSEntry]

@dataclass
class IsolationAttackSettings:
    interface: Interface
    victims: list[Host]
    response_count: int
    response_interval: int