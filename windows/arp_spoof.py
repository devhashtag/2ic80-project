from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from components import HostList, VictimList, InterfaceChooser, Toggle
from attacks import ARPAttackWorker
from util import ARPAttackSettings

class ARPWindow(QWidget):
    INTERFACE_CHOOSER = 'interface_chooser'
    HOST_LIST = 'host_list'
    VICTIMS = 'victims'
    INTERVAL_INPUT = 'interval_input'
    INITIAL_INPUT = 'initial_input'
    ACTIVATION = 'activation'

    stop_attack = pyqtSignal()

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

        # These values are the defaults in Ettercap
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

        self.widgets[self.ACTIVATION].state_changed.connect(self.on_toggle)

    def on_toggle(self, active: bool):
        if active:
            # create the attack
            self.thread = QThread()
            self.worker = ARPAttackWorker(self.construct_attack_settings())
            self.worker.moveToThread(self.thread)

            # connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.stop_attack.connect(self.worker.stop)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.thread.quit)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.finished.connect(lambda: self.widgets[self.ACTIVATION].setEnabled(True))

            # start the attack
            self.thread.start()
        else:
            # stop the attack
            self.widgets[self.ACTIVATION].setEnabled(False)
            self.stop_attack.emit()

    def construct_attack_settings(self) -> ARPAttackSettings:
        victims: VictimList = self.widgets[self.VICTIMS]

        interface = self.widgets[self.INTERFACE_CHOOSER].selected
        sources = victims.widgets[victims.LIST_LEFT].hosts()
        destinations = victims.widgets[victims.LIST_RIGHT].hosts()
        two_way = victims.widgets[victims.RADIO_TWO].isChecked()
        initial = int(self.widgets[self.INITIAL_INPUT].text())
        interval = int(self.widgets[self.INTERVAL_INPUT].text())

        return ARPAttackSettings(interface, sources, destinations, two_way, initial, interval)

