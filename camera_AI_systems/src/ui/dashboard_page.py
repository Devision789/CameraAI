
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QTime, QDate
from PyQt5.QtGui import QFont, QColor
from .memory_usage_chart import MemoryUsageChart

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Tăng khoảng cách giữa các phần tử

        # Header với tên công ty, slogan và thời gian
        header_layout = QHBoxLayout()
        
        # Company name and slogan
        company_info = QVBoxLayout()
        company_name = QLabel("Tiva Solutions")
        company_name.setAlignment(Qt.AlignLeft)
        company_name.setStyleSheet("font-size: 32px; font-weight: bold; color: #4A90E2;")

        slogan = QLabel("Technology Innovation Vision Artificial Intelligence")
        slogan.setAlignment(Qt.AlignLeft)
        slogan.setStyleSheet("font-size: 16px; font-style: italic; color: #7F8C8D;")

        company_info.addWidget(company_name)
        company_info.addWidget(slogan)
        
        header_layout.addLayout(company_info)
        
        # Date and Time
        date_time_layout = QVBoxLayout()
        self.date_label = QLabel()
        self.time_label = QLabel()
        self.date_label.setAlignment(Qt.AlignRight)
        self.time_label.setAlignment(Qt.AlignRight)
        self.date_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2ECC71;")
        self.time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2ECC71;")
        
        date_time_layout.addWidget(self.date_label)
        date_time_layout.addWidget(self.time_label)
        
        header_layout.addLayout(date_time_layout)
        
        layout.addLayout(header_layout)

        # Stats widget
        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(10)  # Tăng khoảng cách giữa các thẻ

        self.create_stat_card("Total Cameras", "12", stats_layout, 0, 0, color="#3498DB")
        self.create_stat_card("Active Cameras", "8", stats_layout, 0, 1, color="#2ECC71", tooltip="Number of cameras currently active.")
        self.create_stat_card("Alerts Today", "5", stats_layout, 0, 2, color="#E74C3C", tooltip="Total alerts triggered today.")
        self.create_stat_card("CPU Usage", "45%", stats_layout, 0, 3, color="#F39C12", tooltip="Current CPU usage percentage.")

        layout.addWidget(stats_widget)

        # Memory usage chart
        self.memory_chart = MemoryUsageChart()
        layout.addWidget(self.memory_chart)

        # Last updated time
        self.update_time_label = QLabel("Last Updated: Just Now")
        self.update_time_label.setAlignment(Qt.AlignRight)
        self.update_time_label.setStyleSheet("font-size: 14px; color: #3498DB;")
        layout.addWidget(self.update_time_label)

        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(1000)

    def create_stat_card(self, title, value, layout, row, col, color=None, tooltip=None):
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #A0A0A0;
            }
        """)
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        value_label = QLabel(value)

        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498DB;")
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")

        if tooltip:
            card.setToolTip(tooltip)

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        layout.addWidget(card, row, col)

    def update_dashboard(self):
        # Cập nhật ngày và giờ
        current_date = QDate.currentDate()
        current_time = QTime.currentTime()
        self.date_label.setText(current_date.toString("dddd, MMMM d, yyyy"))
        self.time_label.setText(current_time.toString("hh:mm:ss AP"))

        # Cập nhật biểu đồ bộ nhớ
        self.memory_chart.plot()

        # Cập nhật thời gian cập nhật cuối cùng
        self.update_time_label.setText(f"Last Updated: {current_time.toString('hh:mm:ss')}")
