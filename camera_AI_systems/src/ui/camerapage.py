import sys
import json
import time
import logging
import cv2
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QFileDialog, QFormLayout,
                            QWidget, QListWidget, QGridLayout, QMessageBox, QScrollArea, 
                            QListWidgetItem, QGroupBox, QProgressBar, QStatusBar, QShortcut)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon, QKeySequence

# Cấu hình logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Các class chính

class CameraConnection(QThread):
    connection_lost = pyqtSignal(int)
    connection_restored = pyqtSignal(int)
    
    def __init__(self, camera_id, camera_info):
        super().__init__()
        self.camera_id = camera_id
        self.camera_info = camera_info
        self.retry_count = 0
        self.max_retries = 3
        self._running = True
        
    def run(self):
        while self._running:
            if not self.check_connection():
                self.connection_lost.emit(self.camera_id)
                self.attempt_reconnect()
            time.sleep(5)
    
    def check_connection(self):
        try:
            # Implement connection check based on protocol
            return True
        except Exception as e:
            logger.error(f"Connection check failed for camera {self.camera_id}: {str(e)}")
            return False
            
    def attempt_reconnect(self):
        while self.retry_count < self.max_retries and self._running:
            try:
                logger.info(f"Attempting to reconnect camera {self.camera_id}")
                # Implement reconnection logic
                self.connection_restored.emit(self.camera_id)
                self.retry_count = 0
                return True
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {str(e)}")
                self.retry_count += 1
                time.sleep(2)
        return False
    
    def stop(self):
        self._running = False


class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Camera")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Camera Name
        self.camera_name = QLineEdit()
        form_layout.addRow("Camera Name:", self.camera_name)

        # Protocol
        self.protocol = QComboBox()
        self.protocol.addItems(["RTSP", "HTTP", "Local File"])
        self.protocol.currentTextChanged.connect(self.on_protocol_changed)
        form_layout.addRow("Protocol:", self.protocol)

        # RTSP URL
        self.rtsp_url = QLineEdit()
        form_layout.addRow("RTSP URL:", self.rtsp_url)

        # IP Address
        self.ip_address = QLineEdit()
        form_layout.addRow("IP Address:", self.ip_address)

        # Port
        self.port = QLineEdit()
        form_layout.addRow("Port:", self.port)

        # Username
        self.username = QLineEdit()
        form_layout.addRow("Username:", self.username)

        # Password
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password)

        # File Path
        self.file_path = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_btn)
        form_layout.addRow("File Path:", file_layout)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        self.apply_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.on_protocol_changed(self.protocol.currentText())

    def validate_and_accept(self):
        try:
            self.validate_camera_info(self.get_camera_info())
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def validate_camera_info(self, info):
        if not info["name"]:
            raise ValueError("Camera name is required")
            
        if info["protocol"] == "RTSP":
            if not info["rtsp_url"].startswith("rtsp://"):
                raise ValueError("Invalid RTSP URL format")
        elif info["protocol"] == "HTTP":
            if not info["ip_address"]:
                raise ValueError("IP address is required for HTTP protocol")
            try:
                port = int(info["port"])
                if port < 0 or port > 65535:
                    raise ValueError("Port must be between 0 and 65535")
            except ValueError:
                raise ValueError("Port must be a valid number")

    def on_protocol_changed(self, protocol):
        is_rtsp = protocol == "RTSP"
        is_http = protocol == "HTTP"
        is_local = protocol == "Local File"

        self.rtsp_url.setVisible(is_rtsp)
        self.ip_address.setVisible(is_http)
        self.port.setVisible(is_http)
        self.username.setVisible(is_rtsp or is_http)
        self.password.setVisible(is_rtsp or is_http)
        self.file_path.setVisible(is_local)
        self.browse_btn.setVisible(is_local)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Video File", 
            "", 
            "Video Files (*.mp4 *.avi *.mov)"
        )
        if file_name:
            self.file_path.setText(file_name)

    def get_camera_info(self):
        protocol = self.protocol.currentText()
        return {
            "name": self.camera_name.text(),
            "protocol": protocol,
            "rtsp_url": self.rtsp_url.text() if protocol == "RTSP" else "",
            "ip_address": self.ip_address.text() if protocol == "HTTP" else "",
            "port": self.port.text() if protocol == "HTTP" else "",
            "username": self.username.text() if protocol in ["RTSP", "HTTP"] else "",
            "password": self.password.text() if protocol in ["RTSP", "HTTP"] else "",
            "file_path": self.file_path.text() if protocol == "Local File" else ""
        }

class CameraView(QLabel):
    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.fullscreen = False
        self.stream = None
        self._is_running = False
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(720, 640)
        self.setStyleSheet("background-color: #2d2d2d;")
        self.setText(f"Camera {self.camera_id}\nDisconnected")
        self.setAlignment(Qt.AlignCenter)
        self.status = "disconnected"
        
                # Add status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(10, 10)
        self.status_indicator.setStyleSheet("""
            QLabel {
                background-color: red;
                border-radius: 5px;
            }
        """)
        
        # Add overlay layout
        overlay = QHBoxLayout()
        overlay.addWidget(self.status_indicator)
        overlay.addStretch()
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(overlay)
        main_layout.addStretch()
        
        
        
            # Add quick actions
        actions_layout = QHBoxLayout()
        
        self.snapshot_btn = QPushButton("📷")
        self.record_btn = QPushButton("⏺")
        self.settings_btn = QPushButton("⚙")
        
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.settings_btn.clicked.connect(self.show_settings)
        
        for btn in [self.snapshot_btn, self.record_btn, self.settings_btn]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.5);
                    border: none;
                    color: white;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.7);
                }
            """)
            actions_layout.addWidget(btn)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)

    def take_snapshot(self):
        # Implement snapshot functionality
        pass

    def toggle_recording(self):
        # Implement recording functionality
        sender = self.sender()
        if sender.isChecked():
            sender.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 0, 0, 0.5);
                }
            """)
        else:
            sender.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.5);
                }
            """)

    def show_settings(self):
        # Implement settings dialog
        pass

    def set_status(self, status):
        self.status = status
        color = "green" if status == "connected" else "red"
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    def start_stream(self):
        if not self._is_running:
            self._is_running = True
            self.stream = cv2.VideoCapture()
            logger.info(f"Started stream for camera {self.camera_id}")

    def stop_stream(self):
        if self._is_running:
            self._is_running = False
            if self.stream:
                self.stream.release()
                self.stream = None
            logger.info(f"Stopped stream for camera {self.camera_id}")

    def update_frame(self, frame):
        self.setPixmap(QPixmap.fromImage(frame))

    def set_status(self, status):
        self.status = status
        color = "green" if status == "connected" else "red"
        self.setText(f"Camera {self.camera_id}\n{status.capitalize()}")
        self.setStyleSheet(f"background-color: #2d2d2d; min-height: 200px; min-width: 200px; color: {color};")
        
    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.setWindowFlags(Qt.Window)
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.setWindowFlags(Qt.Widget)
            self.showNormal()
            self.fullscreen = False

    def closeEvent(self, event):
        self.stop_stream()
        super().closeEvent(event)

class ResultView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("font-size: 14px;")
        
        layout.addWidget(QLabel("Detection Results:"))
        layout.addWidget(self.results_list)

    def update_result(self, license_plate, image):
        item = QListWidgetItem(f"License Plate: {license_plate}")
        item.setIcon(QIcon(QPixmap.fromImage(image)))
        self.results_list.insertItem(0, item)
        if self.results_list.count() > 10:
            self.results_list.takeItem(10)

class CameraPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layout = "3x3"
        self.cameras = {}
        self.camera_connections = {}
        self.init_ui()
        self.load_camera_config()
        self.setup_shortcuts()

    def init_ui(self):
        self.create_layout()
        self.create_left_panel()
        self.create_right_panel()
        self.create_status_bar()


    def create_layout(self):
        self.main_layout = QHBoxLayout(self)

    def create_left_panel(self):
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.create_control_group(left_layout)
        self.create_camera_list(left_layout)
        
        self.main_layout.addWidget(left_panel, 1)

    def create_control_group(self, parent_layout):
        control_group = QGroupBox("Camera Controls")
        control_layout = QVBoxLayout(control_group)
        
        self.create_theme_button(control_layout)
        self.create_grid_controls(control_layout)
        self.create_layout_selector(control_layout)
        self.create_camera_buttons(control_layout)
        
        parent_layout.addWidget(control_group)

    def create_right_panel(self):
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        
        self.create_camera_grid(right_layout)
        self.create_result_view(right_layout)
        
        self.main_layout.addWidget(right_panel, 4)

    def create_camera_grid(self, parent_layout):
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(10)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(grid_widget)
        scroll_area.setWidgetResizable(True)
        
        parent_layout.addWidget(scroll_area, 1)

    def create_result_view(self, parent_layout):
        self.result_view = ResultView()
        parent_layout.addWidget(self.result_view, 1)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.main_layout.addWidget(self.status_bar)

    def setup_shortcuts(self):
        self.connect_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.connect_shortcut.activated.connect(self.connect_camera)
        
        self.disconnect_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.disconnect_shortcut.activated.connect(self.disconnect_camera)

    def save_camera_config(self):
        config = {
            'cameras': self.cameras,
            'layout': self.current_layout
        }
        try:
            with open('camera_config.json', 'w') as f:
                json.dump(config, f)
            logger.info("Camera configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save camera configuration: {str(e)}")
            
    def load_camera_config(self):
        try:
            with open('camera_config.json', 'r') as f:
                config = json.load(f)
                self.cameras = config['cameras']
                self.current_layout = config['layout']
                self.layout_selector.setCurrentText(self.current_layout)
                self.update_camera_list()
            logger.info("Camera configuration loaded successfully")
        except FileNotFoundError:
            logger.info("No camera configuration file found")
        except Exception as e:
            logger.error(f"Failed to load camera configuration: {str(e)}")
            
    def update_camera_list(self):
        self.camera_list.clear()
        for camera_id, camera_info in self.cameras.items():
            self.camera_list.addItem(f"Camera {camera_id}: {camera_info['info']['name']}")



    def add_camera(self):
        dialog = AddCameraDialog(self)
        if dialog.exec_():
            try:
                camera_info = dialog.get_camera_info()
                camera_id = len(self.cameras) + 1
                self.cameras[camera_id] = {
                    "info": camera_info,
                    "connected": False
                }
                self.camera_list.addItem(f"Camera {camera_id}: {camera_info['name']}")
                self.update_grid_layout()
                self.save_camera_config()
                logger.info(f"Added new camera: {camera_info['name']}")
            except Exception as e:
                logger.error(f"Failed to add camera: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to add camera: {str(e)}")


# 2. Xử lý đồng thời
    def connect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            return
            
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        
        try:
            self.loading_spinner.setVisible(True)
            QtCore.QCoreApplication.processEvents()  # Cho phép UI update
            
            worker = CameraWorker(camera_id, self.cameras[camera_id]["info"])
            worker.signals.finished.connect(lambda: self.on_camera_connected(camera_id))
            worker.signals.error.connect(self.on_camera_error)
            
            self.threadpool.start(worker)
            
        except Exception as e:
            logger.error(f"Failed to connect camera {camera_id}: {str(e)}")
            self.loading_spinner.setVisible(False)


    def disconnect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to disconnect.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        
        try:
            if self.cameras[camera_id]["connected"]:
                if camera_id in self.camera_connections:
                    self.camera_connections[camera_id].stop()
                    del self.camera_connections[camera_id]
                
                self.cameras[camera_id]["connected"] = False
                self.update_camera_status(camera_id, "disconnected")
                logger.info(f"Camera {camera_id} disconnected successfully")
                QMessageBox.information(self, "Success", f"Camera {camera_id} disconnected.")
        except Exception as e:
            logger.error(f"Failed to disconnect camera {camera_id}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to disconnect camera: {str(e)}")


    def handle_connection_lost(self, camera_id):
        self.update_camera_status(camera_id, "disconnected")
        self.status_bar.showMessage(f"Connection lost to Camera {camera_id}")
        logger.warning(f"Connection lost to Camera {camera_id}")
        
    def handle_connection_restored(self, camera_id):
        self.update_camera_status(camera_id, "connected")
        self.status_bar.showMessage(f"Connection restored to Camera {camera_id}")
        logger.info(f"Connection restored to Camera {camera_id}")
        

    def update_camera_status(self, camera_id, status):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, CameraView) and widget.camera_id == camera_id:
                widget.set_status(status)
                break
            
    def playback_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera for playback.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        logger.info(f"Starting playback for Camera {camera_id}")
        QMessageBox.information(self, "Playback", f"Starting playback for Camera {camera_id}")

    def filter_cameras(self, text):
        for i in range(self.camera_list.count()):
            item = self.camera_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def change_layout(self, new_layout):
        self.current_layout = new_layout
        self.update_grid_layout()
        self.save_camera_config()
        logger.info(f"Changed layout to {new_layout}")
        
    def update_grid_layout(self):
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Set up new grid
        rows, cols = map(int, self.current_layout.split('x'))
        
        for i, (camera_id, camera_info) in enumerate(self.cameras.items()):
            if i < rows * cols:
                view = CameraView(camera_id)
                if camera_info["connected"]:
                    view.set_status("connected")
                self.grid_layout.addWidget(view, i // cols, i % cols)

        # Resize grid
        grid_widget = self.grid_layout.parentWidget()
        total_width = cols * 210
        total_height = rows * 210
        grid_widget.setFixedSize(total_width, total_height)

    def update_detection_result(self, license_plate, image):
        self.result_view.update_result(license_plate, image)

    # 1. Quản lý tài nguyên
    def closeEvent(self, event):
        try:
            # Thêm timeout để tránh treo
            timeout = 5  # seconds
            start_time = time.time()
            
            for connection in self.camera_connections.values():
                if time.time() - start_time > timeout:
                    logger.warning("Timeout while closing connections")
                    break
                connection.stop()
            
            self.save_camera_config()
            super().closeEvent(event)
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
        finally:
            event.accept()
def main():
    app = QApplication(sys.argv)
    window = CameraPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()