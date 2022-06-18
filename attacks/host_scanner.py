from PyQt6.QtCore import *
from models import Interface, Host
from scapy.all import *

class HostScanner(QObject):
    finished = pyqtSignal(Interface, list)

    def __init__(self, interface: Interface):
        super().__init__()
        self.interface = interface

    def run(self):
        packets = Ether() / ARP()
        packets[Ether].dst = 'ff:ff:ff:ff:ff:ff'
        packets[ARP].pdst = self.interface.subnet

        responses, _ = srp(packets, iface=self.interface.name, timeout=2, verbose=0)

        hosts = [Host(response.psrc, response.hwsrc) for _, response in responses]
        hosts.sort(key=lambda h: reduce(lambda r, e: r*2**8 + int(e), h.ip_addr.split('.'), 0))

        self.finished.emit(self.interface, hosts)