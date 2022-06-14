from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from util import Host

class DragDropHostList(QListWidget):
    """
    QListWidget that has items of type Host and is able
    to work with drag and drops.
    """
    def __init__(self, removable_items=False):
        super().__init__()

        if removable_items:
            self.itemDoubleClicked.connect(lambda _: self.takeItem(self.currentRow()))

    def add_hosts(self, hosts: list[Host]):
        for host in hosts:
            self.add_host(host)

    def add_host(self, host: Host):
        if self.has_host(host):
            return

        item = QListWidgetItem()
        item.setText(host.ip_addr)
        item.setData(Qt.ItemDataRole.UserRole, host)

        self.addItem(item)

    def has_host(self, host: Host):
        return host in self.hosts()

    def hosts(self):
        return [
            self.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.count())
        ]

    def dragEnterEvent(self, event: QDragEnterEvent):
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent):
        event.accept()

    def mimeData(self, items: list[QListWidgetItem]) -> QMimeData:
        encoded = '\n'.join([
            f'{host.ip_addr}|{host.mac_addr}'
            for host in [item.data(Qt.ItemDataRole.UserRole) for item in items]
        ])
        data = QMimeData()
        data.setText(encoded)
        return data

    def dropEvent(self, event: QDropEvent):
        try:
            encoded = event.mimeData().text()
            hosts = [
                Host(host.split('|')[0], host.split('|')[1])
                for host in encoded.split('\n')
            ]

            self.add_hosts(hosts)

            event.accept()
        except:
            # if this does not succeed, the QDropEvent was not
            # for a host. Hence, we just ignore it
            event.ignore()



