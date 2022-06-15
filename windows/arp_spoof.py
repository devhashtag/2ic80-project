from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from components import HostList, VictimList, InterfaceChooser, Toggle

class ARPWindow(QWidget):
    INTERFACE_CHOOSER = 'interface_chooser'
    HOST_LIST = 'host_list'
    VICTIMS = 'victims'
    INTERVAL_INPUT = 'interval_input'
    INITIAL_INPUT = 'initial_input'
    ACTIVATION = 'activation'

    def __init__(self):
        super().__init__()
        self.widgets = { }
        self.layout = self.construct_layout()

        self.setup_behavior()
        self.widgets[self.INTERFACE_CHOOSER].scan()

    def construct_layout(self):
        self.setWindowTitle('ARP attack')
        self.setFixedSize(QSize(800, 500))

        interface = self.widgets[self.INTERFACE_CHOOSER] = InterfaceChooser()
        hosts = self.widgets[self.HOST_LIST] = HostList()
        victims = self.widgets[self.VICTIMS] = VictimList()
        interval = self.widgets[self.INTERVAL_INPUT] = QLineEdit(self)
        initial = self.widgets[self.INITIAL_INPUT] = QLineEdit(self)
        activation = self.widgets[self.ACTIVATION] = Toggle(self, 'Stop', 'Start')

        interval.setText('10')
        initial.setText('4')

        interval.setValidator(QIntValidator())
        initial.setValidator(QIntValidator())

        inputs = QFormLayout()
        inputs.addRow('Initial packets:', initial)
        inputs.addRow('Interval between packets (seconds):', interval)

        settings = QVBoxLayout()
        settings.addLayout(inputs)
        settings.addWidget(activation)

        lhs = QVBoxLayout()
        lhs.addWidget(interface)
        lhs.addWidget(hosts)

        settings_box = QGroupBox()
        settings_box.setTitle('Attack settings')
        settings_box.setLayout(settings)

        rhs = QVBoxLayout()
        rhs.addWidget(victims)
        rhs.addWidget(settings_box)

        layout = QHBoxLayout(self)
        layout.addLayout(lhs)
        layout.addLayout(rhs)

        return layout

    def setup_behavior(self):
        interfaces = self.widgets[self.INTERFACE_CHOOSER]
        hosts = self.widgets[self.HOST_LIST]
        victims = self.widgets[self.VICTIMS]

        interfaces.interface_changed.connect(hosts.set_interface)
        interfaces.interface_changed.connect(lambda _: victims.clear())

        self.widgets[self.ACTIVATION].state_changed.connect(lambda s: print(f'Active: {s}'))