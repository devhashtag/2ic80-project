from .list import DragDropHostList
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import pi
from util import Direction, draw_arrow

class AttackFigure(QWidget):
    """Schematically displays an ARP attack
    """
    ONE_WAY = 'one_way'
    TWO_WAY = 'two_way'

    def __init__(self):
        super().__init__()
        self.attack_mode = self.TWO_WAY

    def set_attack_mode(self, attack_mode: str):
        self.attack_mode = attack_mode
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))

        size = (150, 100)
        offset = event.rect().width() // 2 - size[0] // 2, event.rect().height() // 2 - size[1] // 2

        if self.attack_mode == self.ONE_WAY:
            self.paint_one_way(painter, offset)
        else:
            self.paint_two_way(painter, offset)

        painter.end()

    def paint_one_way(self, painter, offset=(0,0)):
        x, y = offset

        draw_arrow(painter, 150, pi, origin=(x+150, y+50))
        draw_arrow(painter, 60, 0.1*pi, origin=(x+0, y+35))
        draw_arrow(painter, 60, 0.9*pi, origin=(x+150, y+35), direction=Direction.BACKWARDS)

        painter.drawText(QRect(x, y+5, 150, 20), Qt.AlignmentFlag.AlignCenter, 'You')

    def paint_two_way(self, painter, offset=(0,0)):
        x, y = offset

        draw_arrow(painter, 50, 0, (x, y+50), Direction.BOTH)
        draw_arrow(painter, 50, 0, (x+100, y+50), Direction.BOTH)

        painter.drawText(QRect(x+50, y+40, 50, 20), Qt.AlignmentFlag.AlignCenter, 'You')

class VictimList(QGroupBox):
    LIST_LEFT = 'list_left'
    LIST_RIGHT = 'list_right'
    RADIO_ONE = 'radio_one'
    RADIO_TWO = 'radio_two'
    ATTACK_FIGURE = 'figure'
    SWITCH_BUTTON = 'switch'

    def __init__(self):
        super().__init__()
        self.widgets = { }
        self.layout = self.construct_layout()

        self.setup_behavior()

    def construct_layout(self):
        self.setTitle('Victims')
        self.setFixedSize(500, 300)

        list_l = self.widgets[self.LIST_LEFT] = DragDropHostList(removable_items=True)
        list_r = self.widgets[self.LIST_RIGHT] = DragDropHostList(removable_items=True)

        list_l.setAcceptDrops(True)
        list_l.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        list_l.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        list_r.setAcceptDrops(True)
        list_r.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        list_r.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        radio_one = self.widgets[self.RADIO_ONE] = QRadioButton('1-way poisoning')
        radio_two = self.widgets[self.RADIO_TWO] = QRadioButton('2-way poisoning')
        radio_two.setChecked(True)

        attack_figure = self.widgets[self.ATTACK_FIGURE] = AttackFigure()
        attack_figure.setStyleSheet('background-color: green;')

        switch = self.widgets[self.SWITCH_BUTTON] = QPushButton()
        switch.setStyleSheet('background-color: rgba(0,0,0,0)')
        switch.setFixedSize(40, 40)
        switch.setIcon(QIcon('./switch.svg'))
        switch.setIconSize(QSize(32, 32))

        switch.pressed.connect(lambda : switch.setIconSize(QSize(30, 30)))
        switch.clicked.connect(lambda : switch.setIconSize(QSize(32, 32)))

        layout = QGridLayout(self)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 10)
        layout.setRowStretch(3, 1)
        layout.setColumnStretch(0, 10)
        layout.setColumnStretch(1, 13)
        layout.setColumnStretch(2, 10)

        layout.addWidget(list_l, 0, 0, 4, 1)
        layout.addWidget(list_r, 0, 2, 4, 1)

        layout.addWidget(radio_one, 0, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(radio_two, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(attack_figure, 2, 1)
        layout.addWidget(switch, 3, 1, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)

        return layout

    def setup_behavior(self):
        set_attack_mode = lambda mode: lambda: self.widgets[self.ATTACK_FIGURE].set_attack_mode(mode)

        self.widgets[self.RADIO_ONE].pressed.connect(set_attack_mode(AttackFigure.ONE_WAY))
        self.widgets[self.RADIO_TWO].pressed.connect(set_attack_mode(AttackFigure.TWO_WAY))

        self.widgets[self.SWITCH_BUTTON].clicked.connect(self.switch_items)

    def switch_items(self):
        list_l, list_r = self.widgets[self.LIST_LEFT], self.widgets[self.LIST_RIGHT]
        left_hosts = list_l.hosts()
        right_hosts = list_r.hosts()

        self.clear()

        list_l.add_hosts(right_hosts)
        list_r.add_hosts(left_hosts)

    def clear(self):
        self.widgets[self.LIST_LEFT].clear()
        self.widgets[self.LIST_RIGHT].clear()