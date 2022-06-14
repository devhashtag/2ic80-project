from PyQt6.QtWidgets import QApplication
from windows import ARPWindow
import sys


app = QApplication(sys.argv)

window = ARPWindow()
window.show()

app.exec()