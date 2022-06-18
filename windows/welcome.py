from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from windows import ARPWindow, DNSWindow, IsolateWindow

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.construct_layout()

    def construct_layout(self):
        self.setWindowTitle('2IC80 Project')
        self.setFixedSize(QSize(600, 500))

        arp_button = QPushButton(text='ARP spoof attack')
        dns_button = QPushButton(text='DNS spoof attack')
        isolate_button = QPushButton(text='Isolation attack')

        arp_button.clicked.connect(lambda: self.open_window(ARPWindow()))
        dns_button.clicked.connect(lambda: self.open_window(DNSWindow()))
        isolate_button.clicked.connect(lambda: self.open_window(IsolateWindow()))

        layout = QVBoxLayout(self)
        layout.addWidget(arp_button)
        layout.addWidget(dns_button)
        layout.addWidget(isolate_button)

    def open_window(self, window: QWidget):
        self.close()
        self.window = window
        self.window.show()