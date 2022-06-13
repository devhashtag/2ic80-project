from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from util import Interface

ifs = [
    Interface('Wi-Fi', '192.168.2.16', 'fe80::152:6ad6:87de:3ff5%12', '192.168.2.1', '255.255.255.0'),
    Interface('Ethernet', '192.168.2.15', 'de00::152:6ad6:87de:3ff5%12', '192.168.2.1', '255.255.255.0')
]

class InterfaceChooser(QGroupBox):
    IP_DISPLAY = 'ip'
    MAC_DISPLAY = 'mac'
    NETMASK_DISPLAY = 'netmask'
    GATEWAY_DISPLAY = 'gateway'
    NIC_INPUT = 'nic'

    def __init__(self):
        super().__init__()
        self.interfaces = ifs
        self.widgets = { }
        self.layout = self.construct_layout()

        self.setup_behavior()
        self.populate_widgets()

    def construct_layout(self):
        self.setTitle('Interface')
        self.setFixedSize(300, 175)
        

        nic_input = self.widgets[self.NIC_INPUT] = QComboBox()

        ip_display = self.widgets[self.IP_DISPLAY] = QLineEdit()
        ip_display.setDisabled(True)

        mac_display = self.widgets[self.MAC_DISPLAY] = QLineEdit()
        mac_display.setDisabled(True)

        netmask_display = self.widgets[self.NETMASK_DISPLAY] = QLineEdit()
        netmask_display.setDisabled(True)

        gateway_display = self.widgets[self.GATEWAY_DISPLAY] = QLineEdit()
        gateway_display.setDisabled(True)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(3, 2)

        # Extra spacing between NIC selector and the properties
        layout.setRowStretch(1, 0)
        layout.setRowMinimumHeight(1, 10)

        layout.addWidget(QLabel('NIC:'), 0, 0)
        layout.addWidget(nic_input, 0, 1, 1, 3)

        layout.addWidget(QLabel('IP-Address:'), 2, 0, 1, 2)
        layout.addWidget(self.widgets[self.IP_DISPLAY], 2, 2, 1, 2)

        layout.addWidget(QLabel('MAC-Address:'), 3, 0, 1, 2)
        layout.addWidget(mac_display, 3, 2, 1, 2)

        layout.addWidget(QLabel('Netmask:'), 4, 0, 1, 2)
        layout.addWidget(netmask_display, 4, 2, 1, 2)

        layout.addWidget(QLabel('Gateway:'), 5, 0, 1, 2)
        layout.addWidget(gateway_display, 5, 2, 1, 2)

        return layout

    def setup_behavior(self):
        self.widgets[self.NIC_INPUT].currentIndexChanged.connect(lambda _: self.update_display())

    def populate_widgets(self):
        for interface in self.interfaces:
            self.widgets[self.NIC_INPUT].addItem(interface.id, interface)

    def update_display(self):
        interface: Interface = self.widgets[self.NIC_INPUT].currentData()

        self.widgets[self.IP_DISPLAY].setText(interface.ip_addr)
        self.widgets[self.MAC_DISPLAY].setText(interface.mac_addr)
        self.widgets[self.GATEWAY_DISPLAY].setText(interface.gateway)
        self.widgets[self.NETMASK_DISPLAY].setText(interface.netmask)