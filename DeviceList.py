from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QDialogButtonBox


class DeviceList(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/device.ui', self)
        self.setWindowTitle("Choose device?")
        self.buttonBox.addButton("Import", QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
