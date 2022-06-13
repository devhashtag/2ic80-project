from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from util import Interface

class HostList(QGroupBox):
    HOST_LIST = 'hosts'
    REFRESH_BUTTON = 'refresh'

    def __init__(self):
        super().__init__()
        self.interface = None
        self.widgets = { }
        self.layout = self.construct_layout()

        self.setup_behaviour()

    def construct_layout(self):
        self.setTitle('Hosts')
        self.setFixedSize(300, 300)

        layout = QGridLayout(self)

        refresh = QPushButton()
        refresh.setIcon(QIcon('./refresh.svg'))
        refresh.setFixedSize(QSize(44, 22))
        refresh.setStyleSheet('background-color: rgba(0, 0, 0, 0); margin-right: 22px;')
        refresh.setIconSize(QSize(16, 16))
        refresh.pressed.connect(lambda : refresh.setIconSize(QSize(15, 15)))
        refresh.clicked.connect(lambda : refresh.setIconSize(QSize(16, 16)))

        self.widgets[self.REFRESH_BUTTON] = refresh

        self.widgets[self.HOST_LIST] = QListWidget()
        self.widgets[self.HOST_LIST].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        layout.addWidget(self.widgets[self.HOST_LIST], 0, 0)
        layout.addWidget(refresh, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        return layout

    def setup_behaviour(self):
        pass

    def set_interface(self, interface: Interface):
        pass