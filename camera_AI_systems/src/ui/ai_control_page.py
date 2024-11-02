from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QComboBox, QLabel

class AIControlPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        control_panel = QGroupBox("AI Controls")
        control_layout = QVBoxLayout(control_panel)
        
        self.start_ai_btn = QPushButton("Start AI Processing")
        self.stop_ai_btn = QPushButton("Stop AI Processing")
        self.model_select = QComboBox()
        self .model_select.addItems(["YOLOv5", "SSD", "Faster R-CNN"])
        
        control_layout.addWidget(QLabel("Select AI Model:"))
        control_layout.addWidget(self.model_select)
        control_layout.addWidget(self.start_ai_btn)
        control_layout.addWidget(self.stop_ai_btn)
        
        layout.addWidget(control_panel)