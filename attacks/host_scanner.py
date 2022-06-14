from PyQt6.QtCore import *
from attacks import scan_hosts
from util import Interface
import time

class HostScanner(QThread):
    finished = pyqtSignal(Interface, list)

    def __init__(self, interface: Interface):
        super().__init__()
        self.interface = interface

    def run(self):
        hosts = scan_hosts(self.interface)

        self.finished.emit(self.interface, hosts)