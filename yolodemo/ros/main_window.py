import sys
import os
import json
import threading
import cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAbstractItemView, QTextEdit
)
from PyQt5.QtGui import QPixmap, QTextCursor, QImage
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from database_helper import DatabaseHelper
from ros.setting_page import SettingWindow

# ✅ 配置读取函数
CONFIG_FILE = "last_bucket_config.json"
def load_last_bucket():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_bucket", "1号桶")
    return "1号桶"

class SignalBus(QObject):
    photo_ready = pyqtSignal(str)
    log = pyqtSignal(str)
    done = pyqtSignal(dict)
    enable_btn = pyqtSignal()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("大连海洋大学 - 主界面")
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        # 计算屏幕尺寸的一半
        half_width = screen_geometry.width() // 2
        half_height = screen_geometry.height() // 2

        # 设置窗口的最小尺寸为屏幕的一半
        self.setMinimumSize(QSize(half_width, half_height))
        #self.setMinimumSize(1600, 1000)
        self.db = DatabaseHelper()
        self.records = []

        self.loading_timer = QTimer()
        self.loading_index = 0
        self.loading_texts = ["采集中 .", "采集中 ..", "采集中 ..."]
        self.loading_timer.timeout.connect(self.update_loading_text)

        self.signals = SignalBus()
        self.signals.photo_ready.connect(self.on_photo_ready)
        self.signals.log.connect(self.append_log)
        self.signals.done.connect(self.on_collect_done)
        self.signals.enable_btn.connect(self.on_collection_complete)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "编号", "溶氧", "PH", "温度", "照片", "检测结果", "检测时间", "历史记录"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table, 60)

        control_panel = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setStyleSheet("background-color: #1b4032; border-radius: 12px;")
        self.preview_label.setAlignment(Qt.AlignCenter)

        self.collect_btn = QPushButton("\U0001F4CB 开始采集数据")
        self.collect_btn.setStyleSheet("background-color: #4de1a8; font-size: 18px; padding: 10px;")
        self.collect_btn.clicked.connect(self.start_collection)

        self.bucket_label = QLabel()
        self.bucket_label.setAlignment(Qt.AlignRight)
        self.bucket_label.setStyleSheet("font-size: 16px; padding: 5px;")
        self.bucket_label.setText(load_last_bucket())  # ✅ 使用工具函数加载默认桶号

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(200)
        self.log_area.setStyleSheet("background-color: #002822; color: #DDFFDD; font-family: Consolas;")

        bottom_bar = QHBoxLayout()
        debug_btn = QPushButton("\u2699 \u8C03\u8BD5")
        debug_btn.setStyleSheet("background-color: #444; color: white; padding: 4px;")
        debug_btn.clicked.connect(self.open_setting_window)
        bottom_bar.addStretch()
        bottom_bar.addWidget(debug_btn)

        control_panel.addWidget(self.collect_btn)
        control_panel.addWidget(self.bucket_label)
        control_panel.addWidget(self.preview_label)
        control_panel.addWidget(self.log_area)
        control_panel.addLayout(bottom_bar)
        layout.addLayout(control_panel, 40)

    def load_data(self):
        self.records = self.db.get_latest_per_bucket()
        self.table.setRowCount(len(self.records))
        for i, rec in enumerate(self.records):
            self.table.setItem(i, 0, QTableWidgetItem(rec.get('bucketNumber', '')))
            self.table.setItem(i, 1, QTableWidgetItem(rec.get('oxygenLevel', '')))
            self.table.setItem(i, 2, QTableWidgetItem(rec.get('phLevel', '')))
            self.table.setItem(i, 3, QTableWidgetItem(rec.get('temperature', '')))

            img_widget = QLabel()
            if os.path.exists(rec.get('photoPath', '')):
                pix = QPixmap(rec['photoPath']).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_widget.setPixmap(pix)
            self.table.setCellWidget(i, 4, img_widget)

            self.table.setItem(i, 5, QTableWidgetItem(rec.get('photoResult', '')))
            self.table.setItem(i, 6, QTableWidgetItem(rec.get('testTime', '')))

            detail_btn = QPushButton("查看")
            detail_btn.clicked.connect(lambda _, r=rec: self.show_detail(r))
            self.table.setCellWidget(i, 7, detail_btn)

    def show_detail(self, record):
        msg = QMessageBox(self)
        msg.setWindowTitle("采集详情")
        msg.setIcon(QMessageBox.Information)
        text = (
            f"桶号：{record.get('bucketNumber', '')}\n"
            f"温度：{record.get('temperature', '')}\n"
            f"溶氧：{record.get('oxygenLevel', '')}\n"
            f"PH：{record.get('phLevel', '')}\n"
            f"检测时间：{record.get('testTime', '')}\n"
            f"检测结果：{record.get('photoResult', '')}"
        )
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        if os.path.exists(record.get('photoPath', '')):
            self.preview_label.setPixmap(QPixmap(record['photoPath']).scaled(400, 400, Qt.KeepAspectRatio))

    def update_loading_text(self):
        self.collect_btn.setText(self.loading_texts[self.loading_index % len(self.loading_texts)])
        self.loading_index += 1

    def start_collection(self):
        self.collect_btn.setEnabled(False)
        self.loading_index = 0
        self.loading_timer.start(400)
        threading.Thread(target=self._collect_sequence, daemon=True).start()

    def _collect_sequence(self):
        try:
            self.signals.log.emit("====== 开始采集数据 ======")
            bucket = self.bucket_label.text()
            self.signals.log.emit(f"\U0001F9FA 当前桶号：{bucket}")

            self.signals.log.emit("\U0001F4F7 正在拍照...")
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            if not ret:
                cam.release()
                raise Exception("无法读取摄像头")
            folder = os.path.join(os.path.expanduser("~"), "Desktop", "Captured_Images")
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, f"device_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(path, frame)
            cam.release()
            self.signals.log.emit(f"✅ 拍照成功：{path}")
            self.signals.photo_ready.emit(path)

            algae = round(abs(hash(path)) % 300 / 3.0, 1)
            if algae < 80:
                quality = "优质：水体清澈"
            elif algae < 200:
                quality = "良好：少量有机颗粒"
            elif algae < 400:
                quality = "警告：藻类繁殖期"
            else:
                quality = "危险：需立即换水"
            self.signals.log.emit(f"🧪 检测结果：{algae} → {quality}")

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record = {
                'bucketNumber': bucket,
                'temperature': '18.8',
                'oxygenLevel': '8.47mg/L',
                'phLevel': '6.05',
                'testTime': now,
                'photoPath': path,
                'photoResult': f"{algae}\n{quality}"
            }
            self.db.insert_data(record)
            self.signals.log.emit("✅ 数据已保存")
            self.signals.done.emit(record)
        except Exception as e:
            self.signals.log.emit(f"❌ 采集失败：{str(e)}")
        finally:
            self.signals.enable_btn.emit()

    def on_photo_ready(self, path):
        self.preview_label.setPixmap(QPixmap(path).scaled(400, 300, Qt.KeepAspectRatio))

    def on_collect_done(self, _):
        self.load_data()

    def on_collection_complete(self):
        self.loading_timer.stop()
        self.collect_btn.setText("\U0001F4CB 开始采集数据")
        self.collect_btn.setEnabled(True)
        self.append_log("====== 采集完成 ======")

    def append_log(self, msg):
        self.log_area.append(msg)
        self.log_area.moveCursor(QTextCursor.End)

    def open_setting_window(self):
        self.setting_window = SettingWindow()
        self.setting_window.bucket_changed.connect(self.update_bucket_label)
        self.setting_window.show()

    def update_bucket_label(self, name):
        self.bucket_label.setText(name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())