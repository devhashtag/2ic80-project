from PyQt6.QtWidgets import QApplication
from windows import ARPWindow, DNSWindow, IsolateWindow
import sys


app = QApplication(sys.argv)

window = IsolateWindow()
window.show()

app.exec()