from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDateEdit, QPushButton, QTableWidget
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        self.generate_btn = QPushButton("Generate Report")
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        date_layout.addWidget(self.generate_btn)
        
        layout.addWidget(date_widget)
        
        self.report_table = QTableWidget(0, 4)
        self.report_table.setHorizontalHeaderLabels(["Date", "Camera", "Event", "Details"])
        layout.addWidget(self.report_table)