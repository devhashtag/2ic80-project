from PyQt6.QtWidgets import QApplication
from windows import ARPWindow, DNSWindow
import sys


app = QApplication(sys.argv)

window = DNSWindow()
window.show()

app.exec()