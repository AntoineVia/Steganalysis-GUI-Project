import sys
from PyQt6.QtWidgets import QApplication
from Main import App

app = QApplication(sys.argv)
window = App()
window.show()

sys.exit(app.exec())
