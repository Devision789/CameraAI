from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import psutil
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget

class MemoryUsageChart(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(plt.Figure())
        self.layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)

    def plot(self):
        memory = psutil.virtual_memory()
        used_memory = memory.used / (1024 ** 2)  # Convert to MB
        total_memory = memory.total / (1024 ** 2)  # Convert to MB

        self.ax.clear()
        self.ax.pie([used_memory, total_memory - used_memory], labels=['Used', 'Free'], autopct='%1.1f%%')
        self.canvas.draw()