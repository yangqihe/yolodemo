
import sys
import os
import time
import threading
import json
import numpy as np
import serial
import cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PIL import Image, ImageFilter

CONFIG_FILE = "serial_time_config.json"

class DebugPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("调试页面")
        self.resize(1000, 860)

        self.motor_serial = None
        self.oxygen_serial = None
        self.ph_serial = None
        self.camera_on = False
        self.current_bucket = "6号桶"

        self.img_path = "latest_photo.jpg"
        self.temperature = "未知"
        self.ph_value = "未知"
        self.oxygen_value = "未知"
        self.algae_index = ""
        self.water_quality = ""

        self.motor_port = QLineEdit("COM5")
        self.oxygen_port = QLineEdit("COM3")
        self.ph_port = QLineEdit("COM4")
        self.motor_time = QLineEdit("1111")
        self.sensor_time = QLineEdit("111111")

        self.log_output = QTextEdit()
        self.table = QTableWidget(1, 5)
        self.bucket_buttons = {}

        self.init_ui()

    def append_log(self, msg):
        self.log_output.append(msg)

    def init_ui(self):
        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("电机串口:"))
        port_layout.addWidget(self.motor_port)
        port_layout.addWidget(QLabel("溶氧串口:"))
        port_layout.addWidget(self.oxygen_port)
        port_layout.addWidget(QLabel("PH串口:"))
        port_layout.addWidget(self.ph_port)
        save_ports_btn = QPushButton("保存串口配置")
        save_ports_btn.clicked.connect(self.save_port_config)
        port_layout.addWidget(save_ports_btn)
        layout.addLayout(port_layout)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("电机旋转时间:"))
        time_layout.addWidget(self.motor_time)
        time_layout.addWidget(QLabel("传感器测量时间:"))
        time_layout.addWidget(self.sensor_time)
        save_time_btn = QPushButton("保存时间配置")
        save_time_btn.clicked.connect(self.save_time_config)
        time_layout.addWidget(save_time_btn)
        layout.addLayout(time_layout)

        bucket_layout = QHBoxLayout()
        for i in range(1, 7):
            name = f"{i}号桶"
            btn = QPushButton(name)
            self.bucket_buttons[name] = btn
            btn.clicked.connect(lambda _, n=name: self.select_bucket(n))
            bucket_layout.addWidget(btn)
        layout.addLayout(bucket_layout)
        self.select_bucket(self.current_bucket)

        ctrl_grid = QGridLayout()
        labels_cmds = [
            ("打开电机串口", self.open_motor_port),
            ("电机正转", lambda: self.send_motor(0x01)),
            ("舵机正转", lambda: self.send_motor(0x08)),
            ("舵机反转", lambda: self.send_motor(0x02)),
            ("电机反转", lambda: self.send_motor(0x04)),
            ("检测电机", lambda: self.append_log("检测电机中...")),
            ("停止检测电机", lambda: self.append_log("停止检测电机")),
            ("检测舵机", lambda: self.append_log("检测舵机中...")),
            ("停止检测舵机", lambda: self.append_log("停止检测舵机")),
            ("采集数据", self.append_table),
            ("打开溶氧串口", self.open_oxygen_port),
            ("打开PH串口", self.open_ph_port),
            ("读取溶氧", self.read_oxygen),
            ("读取PH", self.read_ph),
            ("打开相机", lambda: self.append_log("📷 相机已打开")),
            ("拍照", self.take_photo),
            ("关闭相机", lambda: self.append_log("📷 相机已关闭")),
        ]
        for i, (label, func) in enumerate(labels_cmds):
            btn = QPushButton(label)
            btn.clicked.connect(func)
            ctrl_grid.addWidget(btn, i // 5, i % 5)
        layout.addLayout(ctrl_grid)

        self.table.setHorizontalHeaderLabels(["编号", "溶氧", "PH", "温度", "照片"])
        layout.addWidget(self.table)

        action_layout = QHBoxLayout()
        detect_btn = QPushButton("检测水质")
        detect_btn.clicked.connect(self.detect_water_quality)
        detect_page_btn = QPushButton("检测水质页面")
        detect_page_btn.clicked.connect(lambda: self.append_log("👉 进入检测水质页面"))
        save_btn = QPushButton("保存采集数据")
        save_btn.clicked.connect(self.save_data)
        action_layout.addWidget(detect_btn)
        action_layout.addWidget(detect_page_btn)
        action_layout.addWidget(save_btn)
        layout.addLayout(action_layout)

        layout.addWidget(QLabel("日志："))
        layout.addWidget(self.log_output)
        self.setLayout(layout)

    def select_bucket(self, name):
        self.current_bucket = name
        for bname, btn in self.bucket_buttons.items():
            btn.setStyleSheet("background-color: lightblue;" if bname == name else "")
        self.append_log(f"✅ 当前选中桶：{name}")
        self.table.setItem(0, 0, QTableWidgetItem(name))

    def save_port_config(self):
        self.append_log("💾 串口配置已保存")
        self.save_config()

    def save_time_config(self):
        self.append_log("💾 时间配置已保存")
        self.save_config()

    def save_config(self):
        data = {
            "motor_port": self.motor_port.text(),
            "oxygen_port": self.oxygen_port.text(),
            "ph_port": self.ph_port.text(),
            "motor_time": self.motor_time.text(),
            "sensor_time": self.sensor_time.text()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

    def open_motor_port(self):
        try:
            self.motor_serial = serial.Serial(self.motor_port.text(), 9600, timeout=1)
            self.append_log("✅ 电机串口已打开")
        except Exception as e:
            self.append_log(f"❌ 电机串口打开失败: {e}")

    def open_oxygen_port(self):
        try:
            self.oxygen_serial = serial.Serial(self.oxygen_port.text(), 9600, timeout=1)
            self.append_log("✅ 溶氧串口已打开")
        except Exception as e:
            self.append_log(f"❌ 溶氧串口打开失败: {e}")

    def open_ph_port(self):
        try:
            self.ph_serial = serial.Serial(self.ph_port.text(), 9600, timeout=1)
            self.append_log("✅ PH串口已打开")
        except Exception as e:
            self.append_log(f"❌ PH串口打开失败: {e}")

    def send_motor(self, cmd):
        try:
            duration = int(self.motor_time.text())
        except ValueError:
            duration = 5
        if self.motor_serial and self.motor_serial.is_open:
            self.motor_serial.write(bytes([cmd]))
            self.append_log(f"📤 已发送指令: 0x{cmd:02X}")
            threading.Thread(target=self.auto_stop_motor, args=(duration,)).start()
        else:
            self.append_log("⚠️ 电机串口未打开")

    def auto_stop_motor(self, delay):
        time.sleep(delay)
        if self.motor_serial and self.motor_serial.is_open:
            self.motor_serial.write(bytes([0x00]))
            self.append_log("🛑 电机已自动停止")

    def take_photo(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.append_log("❌ 无法打开相机")
            return
        ret, frame = cap.read()
        if ret:
            filename = "latest_photo.jpg"
            cv2.imwrite(filename, frame)
            self.img_path = filename
            self.append_log(f"📸 拍照已保存：{filename}")
            self.table.setItem(0, 4, QTableWidgetItem(filename))
        else:
            self.append_log("❌ 拍照失败")
        cap.release()

    def read_oxygen(self):
        if self.oxygen_serial and self.oxygen_serial.is_open:
            try:
                self.oxygen_serial.write(b'R')
                line = self.oxygen_serial.readline().decode().strip()
                self.oxygen_value = line
                self.append_log(f"🌬 溶氧值: {line}")
            except Exception as e:
                self.append_log(f"❌ 读取溶氧失败: {e}")
        else:
            self.append_log("⚠️ 溶氧串口未打开")

    def read_ph(self):
        if self.ph_serial and self.ph_serial.is_open:
            try:
                self.ph_serial.write(b'R')
                line = self.ph_serial.readline().decode().strip()
                self.ph_value = line
                self.append_log(f"🧪 PH值: {line}")
            except Exception as e:
                self.append_log(f"❌ 读取PH失败: {e}")
        else:
            self.append_log("⚠️ PH串口未打开")

    def detect_water_quality(self):
        path = self.img_path
        if not os.path.exists(path):
            self.append_log("⚠️ 无照片，无法分析")
            return
        try:
            img = Image.open(path).convert("RGB")
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
            self.append_log(f"🧪 藻类指数: {self.algae_index} → {self.water_quality}")
        except Exception as e:
            self.append_log(f"❌ 水质检测失败: {e}")

    def append_table(self):
        self.table.setItem(0, 1, QTableWidgetItem(self.oxygen_value))
        self.table.setItem(0, 2, QTableWidgetItem(self.ph_value))
        self.table.setItem(0, 3, QTableWidgetItem(self.temperature))

    def save_data(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.append_log(f"✅ 数据保存成功（时间: {now}）")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DebugPage()
    win.show()
    sys.exit(app.exec_())
