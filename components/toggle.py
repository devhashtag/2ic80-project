from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Toggle(QPushButton):

    state_changed = pyqtSignal(bool)

    def __init__(self, parent=None, on_text = '', off_text=''):
        super().__init__()
        self.on_text = on_text
        self.off_text = off_text
        self.setState(False)

        self.clicked.connect(self.toggle)

    def setState(self, activated: bool):
        self.activated = activated
        self.updateText()
        self.update()

    def updateText(self):
        self.setText(self.on_text if self.activated else self.off_text)

    def toggle(self):
        self.setState(not self.activated)
        self.state_changed.emit(self.activated)

