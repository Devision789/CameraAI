from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt
from .dashboard_page import DashboardPage
from .camera_page import CameraPage
from .ai_control_page import AIControlPage
from .reports_page import ReportsPage
from .styles import ModernStyle
from .settings import SettingsPage

class ModernCameraAISystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Camera AI System")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(ModernStyle.get_stylesheet())
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Navigation bar
        nav_bar = QWidget()
        nav_bar.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav_bar)
        
        self.dashboard_btn = QPushButton("Dashboard")
        self.cameras_btn = QPushButton("Cameras")
        self.ai_control_btn = QPushButton("AI Control")
        self.reports_btn = QPushButton("Reports")
        self.settings_btn = QPushButton("Settings")
        
        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.cameras_btn)
        nav_layout.addWidget(self.ai_control_btn)
        nav_layout.addWidget(self.reports_btn)
        nav_layout.addWidget(self.settings_btn)
        nav_layout.addStretch()

        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.camera_page = CameraPage()
        self.ai_control_page = AIControlPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsPage()
        
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.camera_page)
        self.stacked_widget.addWidget(self.ai_control_page)
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.settings_page)
        

        # Connect navigation buttons
        self.dashboard_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_page))
        self.cameras_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.camera_page))
        self.ai_control_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.ai_control_page))
        self.reports_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.reports_page))
        self.settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))

        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.stacked_widget)

        self.stacked_widget.setCurrentWidget(self.dashboard_page)