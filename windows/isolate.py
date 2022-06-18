from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from attacks import IsolationAttackWorker
from components import HostList, InterfaceChooser, Toggle, DragDropHostList
from scapy.all import *
from util import IsolationAttackSettings

class IsolateWindow(QWidget):
    INTERFACE_CHOOSER = 'interface_chooser'
    HOST_LIST = 'host_list'
    VICTIM_LIST = 'victims'
    ACTIVATION = 'activation'

    stop_attack = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.widgets = { }

        self.construct_layout()
        self.setup_behavior()
        self.widgets[self.INTERFACE_CHOOSER].scan()

    def construct_layout(self):
        self.setWindowTitle('Isolation attack')
        self.setFixedSize(QSize(600, 500))

        interface = self.widgets[self.INTERFACE_CHOOSER] = InterfaceChooser()
        hosts = self.widgets[self.HOST_LIST] = HostList()
        victims = self.widgets[self.VICTIM_LIST] = DragDropHostList(removable_items=True)
        activation = self.widgets[self.ACTIVATION] = Toggle(self, 'Stop', 'Start')

        victims.setAcceptDrops(True)
        victims.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

        sublayout = QVBoxLayout()
        sublayout.addWidget(victims)
        sublayout.addWidget(activation)

        sublayout.setStretch(0, 3)
        sublayout.setStretch(1, 1)

        settings_box = QGroupBox()
        settings_box.setTitle('Attack settings')
        settings_box.setLayout(sublayout)

        layout = QGridLayout(self)
        layout.addWidget(interface, 0, 0)
        layout.addWidget(hosts, 1, 0)
        layout.addWidget(settings_box, 0, 1, 2, 1)

    def setup_behavior(self):
        interface = self.widgets[self.INTERFACE_CHOOSER]
        hosts = self.widgets[self.HOST_LIST]

        interface.interface_changed.connect(hosts.set_interface)

        self.widgets[self.ACTIVATION].state_changed.connect(self.on_toggle)

    def on_toggle(self, active: bool):
        if active:
            self.thread = QThread()
            self.worker = IsolationAttackWorker(IsolationAttackSettings(
                self.widgets[self.INTERFACE_CHOOSER].selected,
                self.widgets[self.VICTIM_LIST].hosts(),
                3,
                1
            ))
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
            self.widgets[self.ACTIVATION].setEnabled(False)
            self.stop_attack.emit()
