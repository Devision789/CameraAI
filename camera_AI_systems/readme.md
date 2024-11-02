1. src/ui/
Module này chứa các thành phần giao diện người dùng (UI) của hệ thống.

__init__.py: File khởi tạo cho package ui.

main_window.py: Chứa class ModernCameraAISystem, là lớp chính cho cửa sổ ứng dụng. Nó thiết lập giao diện chính, bao gồm thanh điều hướng và các trang khác nhau (dashboard, camera, AI control, reports).

dashboard_page.py: Chứa class DashboardPage, hiển thị thông tin tổng quan như thống kê, biểu đồ sử dụng bộ nhớ và các thông tin khác liên quan đến hệ thống.

camera_page.py: Chứa class CameraPage, cung cấp giao diện để quản lý camera, bao gồm tìm kiếm camera, thêm, kết nối và ngắt kết nối camera.

ai_control_page.py: Chứa class AIControlPage, cung cấp giao diện để điều khiển các tính năng AI như khởi động và dừng xử lý AI, cũng như chọn mô hình AI.

reports_page.py: Chứa class ReportsPage, cho phép người dùng tạo báo cáo dựa trên khoảng thời gian đã chọn và hiển thị bảng báo cáo.

styles.py: Chứa các định nghĩa về kiểu dáng (stylesheet) cho ứng dụng, giúp tạo giao diện thống nhất và đẹp mắt.

2. src/core/
Module này chứa các thành phần logic chính của hệ thống.

__init__.py: File khởi tạo cho package core.

camera_manager.py: Chứa class CameraManager, quản lý các camera trong hệ thống. Nó có thể thêm, xóa, kết nối và ngắt kết nối camera.

ai_processor.py: Chứa class AIProcessor, xử lý các khung hình từ camera bằng các mô hình AI đã chọn, thực hiện phân tích và nhận diện đối tượng.

report_generator.py: Chứa logic để tạo báo cáo từ dữ liệu thu thập được từ các camera, bao gồm các sự kiện và thông tin liên quan.

3. src/utils/
Module này chứa các công cụ và tiện ích hỗ trợ cho hệ thống.

__init__.py: File khởi tạo cho package utils.

config.py: Chứa class Config, quản lý cấu hình của ứng dụng. Nó có thể tải các thiết lập từ file cấu hình (ví dụ: YAML) để sử dụng trong toàn bộ ứng dụng.

logger.py: Chứa class Logger, thiết lập và quản lý hệ thống ghi log cho ứng dụng, giúp theo dõi các sự kiện và lỗi xảy ra trong quá trình chạy.

helpers.py: Chứa các hàm tiện ích chung mà có thể được sử dụng ở nhiều nơi trong ứng dụng, như các hàm định dạng dữ liệu hoặc chuyển đổi.

4. src/models/
Module này chứa các mô hình dữ liệu cần thiết cho hệ thống.

__init__.py: File khởi tạo cho package models.

camera.py: Chứa class Camera, đại diện cho một camera trong hệ thống, bao gồm các thuộc tính như ID, URL và trạng thái kết nối.

detection.py: Chứa class Detection, lưu trữ thông tin về các đối tượng được phát hiện trong một khung hình, bao gồm thời gian, camera và danh sách các đối tượng phát hiện.

5. tests/
Module này chứa các bài kiểm tra cho các thành phần của hệ thống.

Các file trong thư mục này sẽ chứa các unit tests cho từng module trong ứng dụng, giúp đảm bảo rằng các chức năng hoạt động đúng.
6. config/
Chứa các file cấu hình cho ứng dụng, có thể là file YAML, JSON hoặc các định dạng khác, giúp quản lý các thông số cấu hình một cách dễ dàng.

7. logs/
Chứa các file log mà hệ thống tạo ra trong quá trình chạy, giúp theo dõi các hoạt động và sự cố.

8. requirements.txt
File này chứa danh sách các thư viện và phiên bản cần thiết để chạy ứng dụng, giúp dễ dàng cài đặt môi trường phát triển và chạy ứng dụng.

