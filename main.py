from PyQt6.QtWidgets import QApplication
from windows import WelcomeWindow
import sys

app = QApplication(sys.argv)

window = WelcomeWindow()
window.show()

app.exec()