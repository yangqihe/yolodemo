import os
import queue
import json
import threading
import time

import numpy as np
import sounddevice as sd
import pyttsx3
import joblib
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel, QDesktopWidget
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from sentence_transformers import SentenceTransformer
from vosk import Model, KaldiRecognizer
from sklearn.metrics.pairwise import cosine_similarity

from sbert.sbert_const import local_huggingface_path

q = queue.Queue()
is_listening = False
rec = None

intent_to_natural_reply = {
    "extend_arm": "转动机械臂",
    "retract_arm": "收回机械臂",
    "extend_sensor": "伸出传感器",
    "retract_sensor": "收回传感器",
    "start_oxygen": "开始测量溶氧",
    "stop_oxygen": "停止测量溶氧",
    "start_ph": "开始测量PH值",
    "stop_ph": "停止PH检测",
    "open_camera": "打开相机",
    "take_photo": "拍照",
    "close_camera": "关闭相机",
}

vosk_model_path = "../model/vosk/vosk-model-cn-0.22"
#vosk_model_path = "../../model/vosk/vosk-model-small-cn-0.22"

if not os.path.exists(vosk_model_path):
    raise FileNotFoundError("❌ 缺少 Vosk 中文模型，请下载解压后放置在当前目录")
rec = KaldiRecognizer(Model(vosk_model_path), 16000)

sbert_index = joblib.load("sbert_intent/intent_sbert_index.pkl")
sbert_model = SentenceTransformer(local_huggingface_path, local_files_only=True)
index_vecs = sbert_index["embeddings"]
index_labels = sbert_index["labels"]
index_texts = sbert_index["texts"]

engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

def short_reply(text):
    if "你是谁" in text:
        return "我是语音助手"
    elif "天气" in text:
        return "我不查天气"
    elif "你好" in text:
        return "你好！"
    else:
        return "你说的是：" + text[:10]

def predict_intent(text, threshold=0.6):
    vec = sbert_model.encode([text])
    sims = cosine_similarity(vec, index_vecs)[0]
    best_idx = np.argmax(sims)
    best_score = sims[best_idx]
    best_label = index_labels[best_idx]
    best_template = index_texts[best_idx]
    if best_score < threshold:
        return "chat", best_score, best_template
    return best_label, best_score, best_template

def speak_async(text):
    print(text)
    # threading.Thread(target=lambda: engine.say(text) or engine.runAndWait(), daemon=True).start()

def audio_callback(indata, frames, time, status):
    if is_listening:
        q.put(bytes(indata))

class VoiceApp(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_frame)
        self.cap = None

        self.setWindowTitle("语音助手")
        self.resize(800, 600)
        self.center_window()

        self.partial_label = QLabel("", self)
        self.partial_label.setStyleSheet("color: gray; font-size: 18px; font-style: italic;")

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("font-size: 16px;")

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: black")

        self.button = QPushButton("🎙️ 开始", self)
        self.button.setStyleSheet("font-size: 16px;")
        self.button.clicked.connect(self.toggle_recognition)

        self.open_camera_button = QPushButton("📷 打开相机", self)
        self.open_camera_button.setStyleSheet("font-size: 16px;")
        self.open_camera_button.clicked.connect(self.show_camera_preview)

        layout = QVBoxLayout()
        layout.addWidget(self.partial_label)
        layout.addWidget(self.text_display)
        layout.addWidget(self.video_label)
        layout.addWidget(self.button)
        layout.addWidget(self.open_camera_button)
        self.setLayout(layout)

        self.stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=4000,
            dtype='int16',
            channels=1,
            callback=audio_callback,
            latency='low'
        )

    def execute_action(self, label):
        if label == "take_photo":
            QTimer.singleShot(0, self.take_photo_with_camera_check)
        elif label == "open_camera":
            QTimer.singleShot(0, self.show_camera_preview)
        elif label == "close_camera":
            QTimer.singleShot(0, self.stop_camera_preview)
        speak_async(f"执行 {label}")

    def take_photo_with_camera_check(self):
        if self.cap is None or not self.cap.isOpened():
            self.show_camera_preview(then_capture=True)
        else:
            self.capture_photo()

    def center_window(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)

    def toggle_recognition(self):
        global is_listening
        if not is_listening:
            self.text_display.clear()
            self.partial_label.setText("")
            self.button.setText("⏹️ 停止")
            is_listening = True
            self.stream.start()
            threading.Thread(target=self.recognition_loop, daemon=True).start()
        else:
            is_listening = False
            self.button.setText("🎙️ 开始")
            self.stream.stop()
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
            try:
                final_result = json.loads(rec.FinalResult())
                text = final_result.get("text", "").strip()
                if text:
                    self.handle_text(text)
            except Exception as e:
                self.text_display.append(f"⚠️ 尾音识别失败：{e}")

    def recognition_loop(self):
        last_partial = ""
        last_partial_time = time.time()
        while is_listening:
            try:
                data = q.get(timeout=1)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                self.partial_label.setText("")
                if text:
                    self.handle_text(text)
            else:
                partial = json.loads(rec.PartialResult())
                ptext = partial.get("partial", "")
                now = time.time()
                if ptext and ptext != last_partial and now - last_partial_time > 0.3:
                    self.partial_label.setText(f"🕓 当前识别：{ptext}")
                    last_partial = ptext
                    last_partial_time = now

    def handle_text(self, text):
        if len(text) < 2:
            print(f"\n识别结果太短：{text}")
            return
        self.text_display.append(f"\n✅ 最终识别结果：{text}")
        label, score, matched = predict_intent(text)
        self.text_display.append(f"🎯 意图：{label}（置信度：{score:.2f}）")
        if label == "chat":
            reply = short_reply(text)
            self.text_display.append(f"💬 回复：{reply}")
            speak_async(reply)
        else:
            reply_text = intent_to_natural_reply.get(label, matched)
            friendly_reply = f"好的，我马上{reply_text}"
            self.text_display.append(f"💬 回复：{friendly_reply}")
            speak_async(friendly_reply)
            self.execute_action(label)
        rec.Reset()

    def update_camera_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.video_label.setPixmap(pixmap)
            else:
                print("⚠️ cap.read() 无法获取帧")
        else:
            print("⚠️ 相机未开启或读取失败")

    def show_camera_preview(self, then_capture=False):
        print("🎥 show_camera_preview 调用")
        if self.cap is not None and self.cap.isOpened():
            print("📸 相机已在运行中")
            return

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.text_display.append("❌ 相机打开失败")
            return

        print("✅ 相机成功打开")
        self.text_display.append("✅ 相机预览已启动")
        self.timer.start(30)

        if then_capture:
            QTimer.singleShot(1500, self.capture_photo)

    def capture_photo(self):
        print('📸 capture_photo 调用')
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                self.text_display.append(f"📸 已保存照片为：{filename}")
            else:
                print("⚠️ 拍照失败：无法读取帧")
        else:
            print("⚠️ 拍照失败：相机未打开")

    def stop_camera_preview(self):
        print("📴 stop_camera_preview")
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.video_label.clear()
            self.text_display.append("📷 相机已关闭")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = VoiceApp()
    window.show()
    sys.exit(app.exec_())
