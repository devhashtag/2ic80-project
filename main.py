print('Importing libraries...')

from tkinter import N
from scapy.all import get_if_list, conf
from PyQt6.QtWidgets import QApplication, QLabel

class Interface:
    def __init__(self, id, ip_address, mac_address, netmask, gateway):
        self.id = None
        self.ip_address = None
        self.mac_address = None
        self.netmask = None
        self.gateway = None

def create_window():
    app = QApplication([])
    label = QLabel('Hello, world!')
    label.show()
    app.exec()

lst = conf.ifaces

print(lst)