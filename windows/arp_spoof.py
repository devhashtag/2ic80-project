from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from components import HostList, VictimList, InterfaceChooser

class ARPWindow(QWidget):
    INTERFACE_CHOOSER = 'interface_chooser'
    HOST_LIST = 'host_list'
    VICTIMS = 'victims'

    def __init__(self):
        super().__init__()
        self.widgets = { }
        self.layout = self.construct_layout()

    def construct_layout(self):
        self.setWindowTitle('ARP attack')
        self.setFixedSize(QSize(1000, 700))

        interface = self.widgets[self.INTERFACE_CHOOSER] = InterfaceChooser()
        hosts = self.widgets[self.HOST_LIST] = HostList()
        victims = self.widgets[self.VICTIMS] = VictimList()

        layout = QGridLayout(self)
        layout.addWidget(interface, 0, 0)
        layout.addWidget(hosts, 1, 0)
        layout.addWidget(victims, 0, 1)

        return layout