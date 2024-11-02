import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import ModernCameraAISystem

def main():
    app = QApplication(sys.argv)
    ex = ModernCameraAISystem()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()