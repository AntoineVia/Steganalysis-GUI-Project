from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QPushButton


class ResultsDisplay(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.perform_setup()

    def perform_setup(self):
        layout = QVBoxLayout()
        result_display = QTableWidget()

        result_display.setColumnCount(2)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)

        layout.addWidget(result_display)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.setWindowTitle("Analysis results")
