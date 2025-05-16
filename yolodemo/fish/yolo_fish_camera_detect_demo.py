from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
from ultralytics import YOLO
import numpy as np
import sys
from sort import Sort

class YOLOFishTracker(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Fish Fry Tracking")
        self.setGeometry(100, 100, 960, 720)

        # 模型和摄像头
        self.model = YOLO('model/best_50s.pt')
        self.cap = cv2.VideoCapture(1)
        self.tracker = Sort()
        self.conf_threshold = 0.3

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.image_label)

        # 启动定时器刷新帧
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # YOLO 检测
        results = self.model(frame)
        dets = []
        for result in results:
            for box in result.boxes:
                if box.conf[0] < self.conf_threshold:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                dets.append([x1, y1, x2, y2])

        # 跟踪
        tracked = self.tracker.update(dets)
        current_ids = set()
        for bbox, track_id in tracked:
            x1, y1, x2, y2 = map(int, bbox)
            current_ids.add(track_id)

            # 画框 + ID
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f'ID {track_id}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # 数量显示（仅统计当前帧中的活跃 ID）
        count_text = f"Unique Fish Fry Count: {len(current_ids)}"
        cv2.putText(frame, count_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Qt 显示
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = YOLOFishTracker()
    window.show()
    sys.exit(app.exec_())
