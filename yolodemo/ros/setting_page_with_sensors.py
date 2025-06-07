
import os
import json
import cv2
import threading
import numpy as np
from PIL import Image, ImageFilter
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, pyqtSignal, Qt

from database_helper import DatabaseHelper

CONFIG_FILE = "last_bucket_config.json"

class SettingPage(QWidget):
    bucket_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("调试页面")
        self.resize(1000, 860)

        self.motor_serial = None
        self.oxygen_serial = None
        self.ph_serial = None
        self.camera = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)

        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.read_sensors)

        self.current_bucket = self.load_last_bucket()
        self.bucket_buttons = {}
        self.img_path = ""
        self.temperature = ""
        self.ph_value = ""
        self.oxygen_value = ""
        self.algae_index = ""
        self.water_quality = ""

        self.init_ui()

    def save_last_bucket(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"last_bucket": self.current_bucket}, f)

    def load_last_bucket(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("last_bucket", "1号桶")
        return "1号桶"

    def set_bucket(self, name):
        self.current_bucket = name
        self.save_last_bucket()
        self.result_display.append(f"✅ 当前选中桶：{name}")
        for bname, btn in self.bucket_buttons.items():
            btn.setStyleSheet("background-color: lightgreen;" if bname == name else "")
        self.bucket_changed.emit(name)

    def save_to_db(self):
        if not self.img_path:
            self.result_display.append("⚠️ 未拍照，无法保存")
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = DatabaseHelper()
        db.insert_data({
            "bucketNumber": self.current_bucket,
            "temperature": self.temperature,
            "oxygenLevel": self.oxygen_value,
            "phLevel": self.ph_value,
            "testTime": now,
            "photoPath": self.img_path,
            "photoResult": f"{self.algae_index} - {self.water_quality}"
        })
        self.result_display.append("✅ 采集数据已保存到数据库")

    def detect_water_quality(self):
        if not self.img_path or not os.path.exists(self.img_path):
            self.result_display.append("⚠️ 无照片，无法分析")
            return
        try:
            img = Image.open(self.img_path).convert("RGB")
            img = img.resize((256, 256)).filter(ImageFilter.GaussianBlur(2))
            green_values = [img.getpixel((x, y))[1] for x in range(img.width) for y in range(img.height)]
            var = np.var(green_values)
            self.algae_index = f"{var:.2f}"
            if var < 80:
                self.water_quality = "优质：水体清澈"
            elif var < 200:
                self.water_quality = "良好：少量有机颗粒"
            elif var < 400:
                self.water_quality = "警告：藻类繁殖期"
            else:
                self.water_quality = "危险：需立即换水"
            self.result_display.append(f"🧪 藻类指数: {self.algae_index} → {self.water_quality}")
        except Exception as e:
            self.result_display.append(f"❌ 水质检测失败: {e}")

    def init_ui(self):
        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        self.motor_port_input = QLineEdit("COM5")
        self.oxygen_port_input = QLineEdit("COM3")
        self.ph_port_input = QLineEdit("COM4")
        for w, label in zip([self.motor_port_input, self.oxygen_port_input, self.ph_port_input],
                            ["电机串口:", "溶氧串口:", "PH串口:"]):
            port_layout.addWidget(QLabel(label))
            port_layout.addWidget(w)
        layout.addLayout(port_layout)

        sensor_port_layout = QHBoxLayout()
        self.open_oxygen_btn = QPushButton("打开溶氧串口")
        self.open_ph_btn = QPushButton("打开PH串口")
        self.open_oxygen_btn.clicked.connect(self.open_oxygen_port)
        self.open_ph_btn.clicked.connect(self.open_ph_port)
        sensor_port_layout.addWidget(self.open_oxygen_btn)
        sensor_port_layout.addWidget(self.open_ph_btn)
        layout.addLayout(sensor_port_layout)

        bucket_layout = QHBoxLayout()
        for i in range(1, 7):
            bucket_name = f"{i}号桶"
            btn = QPushButton(bucket_name)
            self.bucket_buttons[bucket_name] = btn
            btn.clicked.connect(lambda _, b=bucket_name: self.set_bucket(b))
            bucket_layout.addWidget(btn)
        layout.addLayout(bucket_layout)

        if self.current_bucket in self.bucket_buttons:
            self.bucket_buttons[self.current_bucket].setStyleSheet("background-color: lightgreen;")

        motor_layout = QHBoxLayout()
        self.open_motor_btn = QPushButton("打开电机串口")
        self.open_motor_btn.clicked.connect(self.toggle_motor)
        motor_layout.addWidget(self.open_motor_btn)
        for label, cmd in [("电机正转", 0x01), ("舵机正转", 0x08), ("舵机反转", 0x02), ("电机反转", 0x04)]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, c=cmd: self.send_motor_command(c))
            motor_layout.addWidget(btn)
        layout.addLayout(motor_layout)

        cam_layout = QHBoxLayout()
        self.open_cam_btn = QPushButton("打开相机")
        self.take_photo_btn = QPushButton("拍照")
        self.close_cam_btn = QPushButton("关闭相机")
        self.take_photo_btn.clicked.connect(self.capture_photo)
        self.open_cam_btn.clicked.connect(self.open_camera)
        self.close_cam_btn.clicked.connect(self.close_camera)
        cam_layout.addWidget(self.open_cam_btn)
        cam_layout.addWidget(self.take_photo_btn)
        cam_layout.addWidget(self.close_cam_btn)
        layout.addLayout(cam_layout)

        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)
        self.image_label.setStyleSheet("background-color: black")
        layout.addWidget(self.image_label)

        self.result_display = QTextEdit()
        layout.addWidget(self.result_display)

        self.table = QTableWidget(1, 5)
        self.table.setHorizontalHeaderLabels(["编号", "溶氧", "PH", "温度", "照片"])
        layout.addWidget(self.table)

        data_btns = QHBoxLayout()
        self.detect_btn = QPushButton("检测水质")
        self.save_btn = QPushButton("保存采集数据")
        self.detect_btn.clicked.connect(self.detect_water_quality)
        self.save_btn.clicked.connect(self.save_to_db)
        data_btns.addWidget(self.detect_btn)
        data_btns.addWidget(self.save_btn)
        layout.addLayout(data_btns)

        self.setLayout(layout)

    def open_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.timer.start(30)
                self.result_display.append("📷 相机已打开")
            else:
                self.result_display.append("❌ 无法打开相机")

    def update_camera_frame(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(img))

    def capture_photo(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret:
                filename = f"photo_{self.current_bucket}_{int(threading.get_ident())}.jpg"
                cv2.imwrite(filename, frame)
                self.img_path = filename
                self.result_display.append(f"📸 拍照已保存：{filename}")
                self.table.setItem(0, 0, QTableWidgetItem(self.current_bucket))
                self.table.setItem(0, 4, QTableWidgetItem(filename))

    def close_camera(self):
        if self.camera:
            self.timer.stop()
            self.camera.release()
            self.camera = None
            self.image_label.clear()
            self.result_display.append("📷 相机已关闭")

    def toggle_motor(self):
        import serial
        port_name = self.motor_port_input.text().strip()
        if self.motor_serial and self.motor_serial.is_open:
            self.motor_serial.close()
            self.result_display.append(f"❎ 已关闭串口 {port_name}")
        else:
            try:
                self.motor_serial = serial.Serial(port=port_name, baudrate=9600, timeout=1)
                self.result_display.append(f"✅ 已打开串口 {port_name}")
            except Exception as e:
                self.result_display.append(f"❌ 打开串口失败: {e}")

    def send_motor_command(self, command_byte):
        if self.motor_serial and self.motor_serial.is_open:
            self.motor_serial.write(bytes([command_byte]))
            self.result_display.append(f"📤 已发送指令: 0x{command_byte:02X}")
        else:
            self.result_display.append("⚠️ 电机串口未打开")

    def open_oxygen_port(self):
        import serial
        port_name = self.oxygen_port_input.text().strip()
        try:
            self.oxygen_serial = serial.Serial(port=port_name, baudrate=9600, timeout=1)
            self.result_display.append(f"✅ 溶氧串口已打开: {port_name}")
            self.start_sensor_timer()
        except Exception as e:
            self.result_display.append(f"❌ 溶氧串口打开失败: {e}")

    def open_ph_port(self):
        import serial
        port_name = self.ph_port_input.text().strip()
        try:
            self.ph_serial = serial.Serial(port=port_name, baudrate=9600, timeout=1)
            self.result_display.append(f"✅ PH串口已打开: {port_name}")
            self.start_sensor_timer()
        except Exception as e:
            self.result_display.append(f"❌ PH串口打开失败: {e}")

    def start_sensor_timer(self):
        if not self.sensor_timer.isActive():
            self.sensor_timer.start(1000)

    def read_sensors(self):
        try:
            if self.oxygen_serial and self.oxygen_serial.is_open:
                self.oxygen_serial.write(b'R')
                line = self.oxygen_serial.readline().decode(errors='ignore').strip()
                if line:
                    self.oxygen_value = line
                    self.result_display.append(f"🌬 溶氧值: {line}")
                    self.table.setItem(0, 1, QTableWidgetItem(line))
        except Exception as e:
            self.result_display.append(f"❌ 溶氧读取失败: {e}")

        try:
            if self.ph_serial and self.ph_serial.is_open:
                self.ph_serial.write(b'R')
                line = self.ph_serial.readline().decode(errors='ignore').strip()
                if line:
                    self.ph_value = line
                    self.result_display.append(f"🧪 PH值: {line}")
                    self.table.setItem(0, 2, QTableWidgetItem(line))
        except Exception as e:
            self.result_display.append(f"❌ PH读取失败: {e}")


class SettingWindow(QDialog):
    bucket_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("调试页面")
        self.setMinimumSize(1000, 860)
        self.setWindowModality(Qt.ApplicationModal)

        self.inner_widget = SettingPage()
        layout = QVBoxLayout()
        layout.addWidget(self.inner_widget)
        self.setLayout(layout)

        self.inner_widget.bucket_changed.connect(self.bucket_changed)
