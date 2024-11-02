class ModernStyle:
    DARK_PRIMARY = "#1a1a1a"
    DARK_SECONDARY = "#2d2d2d"
    LIGHT_PRIMARY = "#ffffff"
    LIGHT_SECONDARY = "#f5f5f5"
    ACCENT = "#2196F3"
    ACCENT_HOVER = "#1976D2"

    @staticmethod
    def get_stylesheet():
        return """
        QMainWindow, QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        QPushButton {
            background-color: #2196F3;
            border: none;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QLabel, QGroupBox {
            color: #ffffff;
        }
        QGroupBox {
            border: 1px solid #2d2d2d;
            border-radius: 4px;
            margin-top: 1em;
            padding-top: 1em;
        }
        QListWidget, QTextEdit, QTableWidget {
            background-color: #2d2d2d;
            border: none;
            border-radius: 4px;
        }
        QLineEdit {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #2d2d2d;
            border-radius: 4px;
            padding: 5px;
        }
        QCalendarWidget {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QCalendarWidget QToolButton {
            color: #ffffff;
            background-color: #2196F3;
        }
        QCalendarWidget QMenu {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QDateEdit {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #2d2d2d;
            border-radius: 4px;
            padding: 5px;
        }
        """