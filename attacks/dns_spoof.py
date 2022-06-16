from tkinter import W
from attacks.arp_spoof import ARPAttackSettings
from dataclasses import dataclass
from scapy.all import *

@dataclass
class DNSEntry:
    url: str
    type: str
    ip: str

@dataclass
class DNSAttackSettings:
    arp_settings: ARPAttackSettings
    dns_rules: list[DNSEntry]

def handle_packet(settings: DNSAttackSettings, packet: Packet):

    print(packet.summary())
    # We only handle packets that have UDP, IP and DNS protocols
    # Packet must contain DNS query and IP layer
    if not (DNS in packet and IP in packet and UDP in packet):
        return

    # check for dns standard query
    if packet[DNS].opcode != 0:
        return

    

    # check queries
    # DNS query must match