from .list import DragDropHostList
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from attacks.host_scanner import HostScanner
from util import Interface, Host

class HostList(QGroupBox):
    HOST_LIST = 'hosts'
    REFRESH_BUTTON = 'refresh'

    def __init__(self):
        super().__init__()
        self.interface = None
        self.widgets = { }
        self.is_scanning = False
        self.layout = self.construct_layout()

        self.setup_behaviour()

    def construct_layout(self):
        self.setTitle('Hosts')
        self.setFixedSize(300, 300)

        layout = QGridLayout(self)

        refresh = QPushButton()
        refresh.setIcon(QIcon('./refresh.svg'))
        refresh.setFixedSize(QSize(44, 22))
        refresh.setStyleSheet('background: transparent; border: 0; margin-right: 22px;')
        refresh.setIconSize(QSize(16, 16))
        refresh.pressed.connect(lambda: refresh.setIconSize(QSize(15, 15)))
        refresh.clicked.connect(lambda: refresh.setIconSize(QSize(16, 16)))

        self.widgets[self.REFRESH_BUTTON] = refresh

        host_list = self.widgets[self.HOST_LIST] = DragDropHostList()
        host_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        host_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        host_list.setAcceptDrops(True)
        host_list.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

        layout.addWidget(self.widgets[self.HOST_LIST], 0, 0)
        layout.addWidget(refresh, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        return layout

    def setup_behaviour(self):
        self.widgets[self.REFRESH_BUTTON].clicked.connect(self.start_scanning)

    def start_scanning(self):
        if self.is_scanning:
            print('Hosts are already being scanned')
            return

        if self.interface is None:
            print('To scan hosts, select an interface first')
            return

        self.is_scanning = True
        self.setDisabled(True)

        host_list = self.widgets[self.HOST_LIST]
        host_list.clear()

        self._scanner = HostScanner(self.interface)
        self._scanner.finished.connect(self.stop_scanning)
        self._scanner.start()

    def stop_scanning(self, interface, hosts):
        # Join thread before removing the reference to it
        self._scanner.wait()
        self._scanner = None

        # only add the hosts if the interface has not changed
        # during the scan
        if interface == self.interface:
            for host in hosts:
                self.widgets[self.HOST_LIST].add_host(host)

        self.setDisabled(False)
        self.is_scanning = False

    def set_interface(self, interface: Interface):
        self.interface = interface
        self.widgets[self.HOST_LIST].clear()