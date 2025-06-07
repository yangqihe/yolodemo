# 主程序新增：集成水质检测与SQLite数据保存功能
import sys
import os
import json
import queue
import threading
import cv2
import numpy as np
import serial
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit,
                             QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem,
                             QGridLayout, QGroupBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from vosk import Model, KaldiRecognizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image, ImageFilter

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("语音+串口+拍照控制台")
        self.resize(1000, 860)

        self.queue = queue.Queue()
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.embeddings_data = self.load_embeddings()
        self.vosk_model = KaldiRecognizer(Model("vosk-model-cn-0.22"), 16000)

        self.motor_serial = None
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)

        self.current_bucket = "1号桶"
        self.img_path = ""
        self.temperature = ""
        self.ph_value = ""
        self.oxygen_value = ""
        self.algae_index = ""
        self.water_quality = ""

        self.init_db()
        self.init_ui()

    def init_db(self):
        conn = sqlite3.connect("collected_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bucket TEXT,
                temperature TEXT,
                oxygen TEXT,
                ph TEXT,
                test_time TEXT,
                photo TEXT,
                algae_index TEXT,
                water_quality TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_to_db(self):
        if not self.img_path:
            self.result_display.append("⚠️ 未拍照，无法保存")
            return
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("collected_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO data (bucket, temperature, oxygen, ph, test_time, photo, algae_index, water_quality)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.current_bucket, self.temperature, self.oxygen_value, self.ph_value,
              now, self.img_path, self.algae_index, self.water_quality))
        conn.commit()
        conn.close()
        self.result_display.append("✅ 采集数据已保存到数据库")

    def detect_water_quality(self):
        if not self.img_path or not os.path.exists(self.img_path):
            self.result_display.append("⚠️ 无照片，无法分析")
            return
        try:
            img = Image.open(self.img_path).convert("RGB")
            img = img.resize((256, 256)).filter(ImageFilter.GaussianBlur(2))
            green_values = []
            for x in range(img.width):
                for y in range(img.height):
                    r, g, b = img.getpixel((x, y))
                    green_values.append(g)
            avg = np.mean(green_values)
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
        port_layout.addWidget(QLabel("电机串口:"))
        port_layout.addWidget(self.motor_port_input)
        port_layout.addWidget(QLabel("溶氧串口:"))
        port_layout.addWidget(self.oxygen_port_input)
        port_layout.addWidget(QLabel("PH串口:"))
        port_layout.addWidget(self.ph_port_input)
        layout.addLayout(port_layout)

        bucket_layout = QHBoxLayout()
        for i in range(1, 7):
            btn = QPushButton(f"{i}号桶")
            btn.clicked.connect(lambda _, b=f"{i}号桶": self.set_bucket(b))
            bucket_layout.addWidget(btn)
        layout.addLayout(bucket_layout)

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

    def set_bucket(self, name):
        self.current_bucket = name
        self.result_display.append(f"✅ 当前选中桶：{name}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
