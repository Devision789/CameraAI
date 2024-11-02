 
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

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        self.ai_mode = "None"  # Default AI mode
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(640, 640)
        self.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 5px;
            }
        """)
        self.setText(f"Camera {self.camera_id}\nDisconnected")
        self.setAlignment(Qt.AlignCenter)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add AI mode selector
        ai_control_layout = QHBoxLayout()
        
        # Camera ID Label
        camera_label = QLabel(f"Camera {self.camera_id}")
        camera_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                font-weight: bold;
                border: none;
            }
        """)
        
        # AI Mode Selector
        self.ai_mode_selector = QComboBox()
        self.ai_mode_selector.addItems([
            "None", 
            "License Plate Detection",
            "Face Detection",
            "Object Detection",
            "Motion Detection"
        ])
        self.ai_mode_selector.setStyleSheet("""
            QComboBox {
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
                min-width: 150px;
            }
            QComboBox:hover {
                background-color: rgba(0, 0, 0, 0.7);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #404040;
                border: 1px solid #555555;
            }
        """)
        self.ai_mode_selector.currentTextChanged.connect(self.change_ai_mode)
        
        ai_control_layout.addWidget(camera_label)
        ai_control_layout.addWidget(self.ai_mode_selector)
        ai_control_layout.addStretch()
        
        main_layout.addLayout(ai_control_layout)
        main_layout.addStretch()

    def change_ai_mode(self, mode):
        """Handle AI mode change"""
        self.ai_mode = mode
        logger.info(f"Camera {self.camera_id} AI mode changed to: {mode}")
        # Implement AI mode change logic here
        
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
        """Update the camera frame"""
        self.setPixmap(QPixmap.fromImage(frame))

    def set_status(self, status):
        """Update camera status"""
        if status == "connected":
            self.setText("")  # Clear text when connected
        else:
            self.setText(f"Camera {self.camera_id}\nDisconnected")
            
    def mouseDoubleClickEvent(self, event):
        """Handle double click for fullscreen"""
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if not self.fullscreen:
            self.setWindowFlags(Qt.Window)
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.setWindowFlags(Qt.Widget)
            self.showNormal()
            self.fullscreen = False

    def closeEvent(self, event):
        """Handle close event"""
        self.stop_stream()
        super().closeEvent(event)
class ResultView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set fixed width to be half of original (assuming original matches camera view width)
        self.setFixedWidth(320)  # Half of 640
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        
        # Title label with styling
        title_label = QLabel("Detection Results")
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333333;
                padding: 5px;
            }
        """)
        
        # Results list with styling
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                font-size: 12px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e6e6e6;
                color: black;
            }
        """)
        

        
        layout.addWidget(title_label)
        layout.addWidget(self.results_list)

    def update_result(self, license_plate, image):
        item = QListWidgetItem(f"License: {license_plate}")
        
        # Scale down the image to fit the narrower width
        scaled_image = image.scaledToWidth(280)  # Slightly less than widget width
        item.setIcon(QIcon(QPixmap.fromImage(scaled_image)))
        
        self.results_list.insertItem(0, item)
        if self.results_list.count() > 10:
            self.results_list.takeItem(10)

class CameraPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layout = "2x2"  # Đặt layout mặc định là 2x2
        self.cameras = {}
        self.camera_connections = {}
        self.init_ui()
        self.load_camera_config()
        self.setup_shortcuts()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Controls
        control_group = QGroupBox("Camera Controls")
        control_layout = QVBoxLayout(control_group)

        # Thêm nút toggle theme
        self.theme_btn = QPushButton()
        self.theme_btn.setCheckable(True)
        self.theme_btn.clicked.connect(self.toggle_theme)
        control_layout.addWidget(self.theme_btn)

        # Thêm vào class CameraPage trong init_ui()
        grid_controls = QWidget()
        grid_controls_layout = QHBoxLayout(grid_controls)

        self.reset_btn = QPushButton("Reset") 
        self.delete_btn = QPushButton("Delete Camera")  # Nút xóa camera

        self.reset_btn.clicked.connect(self.reset_system)
        self.delete_btn.clicked.connect(self.delete_camera)  # Kết nối nút xóa camera

        grid_controls_layout.addWidget(self.reset_btn)
        grid_controls_layout.addWidget(self.delete_btn)  # Thêm nút xóa vào layout

        control_layout.addWidget(grid_controls)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Camera...")
        self.search_bar.textChanged.connect(self.filter_cameras)
        
        self.camera_list = QListWidget()
        
        self.layout_selector = QComboBox()
        self.layout_selector.addItems(["2x2", "3x3", "4x4", "2x3", "3x2"])
        self.layout_selector.setCurrentText(self.current_layout)
        self.layout_selector.currentTextChanged.connect(self.change_layout)
        
        control_layout.addWidget(QLabel("Select Layout:"))
        control_layout.addWidget(self.layout_selector)
        
        self.loading_spinner = QProgressBar()
        self.loading_spinner.setVisible(False)
        
        self.current_page = 1
        self.total_pages = 1
        
        self.prev_page_btn = QPushButton("◄")
        self.next_page_btn = QPushButton("►")
        self.page_label = QLabel(f"Page {self.current_page}/{self.total_pages}")
        
        self.prev_page_btn.clicked.connect(self.previous_page)
        self.next_page_btn.clicked.connect(self.next_page)
        
        grid_controls_layout.addWidget(self.prev_page_btn)
        grid_controls_layout.addWidget(self.page_label)
        grid_controls_layout.addWidget(self.next_page_btn)
        self.add_btn = QPushButton("Add Camera")
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.playback_btn = QPushButton("Playback")
        
        self.add_btn.clicked.connect(self.add_camera)
        self.connect_btn.clicked.connect(self.connect_camera)
        self.disconnect_btn.clicked.connect(self.disconnect_camera)
        self.playback_btn.clicked.connect(self.playback_camera)
        
        for btn in [self.add_btn, self.connect_btn, self.disconnect_btn, self.playback_btn]:
            control_layout.addWidget(btn)
        
        control_layout.addWidget(self.loading_spinner)
        
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.camera_list)
        left_layout.addWidget(control_group)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(10)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(grid_widget)
        scroll_area.setWidgetResizable(True)
        
        self.result_view = ResultView()
        
        right_layout.addWidget(scroll_area, 3)
        right_layout.addWidget(self.result_view, 1)
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 5)
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_grid_layout()
            self.update_page_controls()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_grid_layout()
            self.update_page_controls()

    def update_page_controls(self):
        self.page_label.setText(f"Page {self.current_page}/{self.total_pages}")
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)

    def reset_system(self):
        """Reset all camera configurations and connections."""
        # Dừng tất cả các kết nối camera
        for connection in self.camera_connections.values():
            connection.stop()
        
        # Xóa tất cả camera
        self.cameras.clear()
        self.camera_connections.clear()
        self.camera_list.clear()
        
        # Khôi phục lại giao diện
        self.current_layout = "2x2"
        self.layout_selector.setCurrentText(self.current_layout)
        self.update_grid_layout()
        
        logger.info("System reset successfully")
        QMessageBox.information(self, "Reset", "System has been reset successfully.")
    def delete_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to delete.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[ 0].split()[-1])
        
        try:
            del self.cameras[camera_id]
            self.camera_list.takeItem(self.camera_list.row(selected_items[0]))
            self.update_grid_layout()
            self.save_camera_config()
            logger.info(f"Deleted camera {camera_id}")
            QMessageBox.information(self, "Success", f"Deleted camera {camera_id}")
        except Exception as e:
            logger.error(f"Failed to delete camera {camera_id}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete camera: {str(e)}")

    def save_camera_config(self):
        """Save the current camera configuration to a file."""
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
        """Load the camera configuration from a file."""
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
    
    # Thêm phương thức toggle_theme
    def toggle_theme(self):
        if self.theme_btn.isChecked():
            # Dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #404040;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QLineEdit {
                    background-color: #404040;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QComboBox {
                    background-color: #404040;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #404040;
                    border: 1px solid #555555;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                }
            """)

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

    def connect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to connect.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        
        try:
            self.loading_spinner.setVisible(True)
            if not self.cameras[camera_id]["connected"]:
                camera_info = self.cameras[camera_id]["info"]
                
                # Start camera connection thread
                connection = CameraConnection(camera_id, camera_info)
                connection.connection_lost.connect(self.handle_connection_lost)
                connection.connection_restored.connect(self.handle_connection_restored)
                self.camera_connections[camera_id] = connection
                connection.start()
                
                self.cameras[camera_id]["connected"] = True
                self.update_camera_status(camera_id, "connected")
                logger.info(f"Camera {camera_id} connected successfully")
                QMessageBox.information(self, "Success", f"Camera {camera_id} connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect camera {camera_id}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to connect camera: {str(e)}")
        finally:
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

        # Calculate total pages needed
        cameras_per_page = 4  # 2x2 grid
        total_cameras = len(self.cameras)
        self.total_pages = (total_cameras + cameras_per_page - 1) // cameras_per_page
        
        # Update page controls
        self.update_page_controls()
        
        # Calculate start and end indices for current page
        start_idx = (self.current_page - 1) * cameras_per_page
        end_idx = min(start_idx + cameras_per_page, total_cameras)
        
        # Add cameras for current page
        rows, cols = 2, 2
        grid_position = 0
        
        for i, (camera_id, camera_info) in enumerate(self.cameras.items()):
            if start_idx <= i < end_idx:
                view = CameraView(camera_id)
                if camera_info["connected"]:
                    view.set_status("connected")
                self.grid_layout.addWidget(view, grid_position // cols, grid_position % cols)
                grid_position += 1

        # Resize grid
        grid_widget = self.grid_layout.parentWidget()
        total_width = cols * 640
        total_height = rows * 640
        grid_widget.setFixedSize(total_width, total_height)

    def update_detection_result(self, license_plate, image):
        self.result_view.update_result(license_plate, image)

    def closeEvent(self, event):
        try:
            # Stop all camera connections
            for connection in self.camera_connections.values():
                connection.stop()
            
            # Save configuration
            self.save_camera_config()
            
            logger.info("Application shutting down")
            event.accept()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = CameraPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()