import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

class CameraPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("相机预览测试")
        self.setFixedSize(700, 550)

        self.label = QLabel("加载中...", self)
        self.label.setFixedSize(640, 480)
        self.label.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 对于 Windows 推荐 CAP_DSHOW

        if not self.cap.isOpened():
            self.label.setText("❌ 无法打开摄像头")
            return

        print("✅ 相机已打开")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 每 30 毫秒刷新一次

    def update_frame(self):
        print("⏳ 刷新帧")  # 用于调试
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    preview = CameraPreview()
    preview.show()
    sys.exit(app.exec_())
