import os
import queue
import json
import threading
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

vosk_model_path = "../../model/vosk/vosk-model-cn-0.22"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError("❌ 缺少 Vosk 中文模型，请下载解压后放置在当前目录")
rec = KaldiRecognizer(Model(vosk_model_path), 16000)

sbert_index = joblib.load("sbert_intent/intent_sbert_index.pkl")
sbert_model = SentenceTransformer(sbert_index["model_name"])
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

def execute_action(label):
    if label == "take_photo":
        window.show_camera_preview()
    elif label == "open_camera":
        window.show_camera_preview()
    elif label == "close_camera":
        window.stop_camera_preview()
    else:
        print(f"🦾 执行动作：{label}")
        engine.say(f"执行 {label}")
        engine.runAndWait()

def audio_callback(indata, frames, time, status):
    if is_listening:
        q.put(bytes(indata))

class VoiceApp(QWidget):
    def __init__(self):
        super().__init__()
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

        layout = QVBoxLayout()
        layout.addWidget(self.partial_label)
        layout.addWidget(self.text_display)
        layout.addWidget(self.video_label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.stream = sd.RawInputStream(device=None, samplerate=16000, blocksize=8000,
                                        dtype='int16', channels=1, callback=audio_callback)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)

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
                if ptext and ptext != last_partial:
                    self.partial_label.setText(f"🕓 当前识别：{ptext}")
                    last_partial = ptext

    def handle_text(self, text):
        self.text_display.append(f"\n✅ 最终识别结果：{text}")
        label, score, matched = predict_intent(text)
        self.text_display.append(f"🎯 意图：{label}（置信度：{score:.2f}）")
        if label == "chat":
            reply = short_reply(text)
            self.text_display.append(f"💬 回复：{reply}")
            engine.say(reply)
            engine.runAndWait()
        else:
            reply_text = intent_to_natural_reply.get(label, matched)
            friendly_reply = f"好的，我马上{reply_text}"
            self.text_display.append(f"💬 回复：{friendly_reply}")
            engine.say(friendly_reply)
            engine.runAndWait()
            execute_action(label)
            if label == "take_photo":
                QTimer.singleShot(1500, self.capture_photo)  # 拍照延时1.5秒

    def show_camera_preview(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.text_display.append("❌ 相机打开失败")
                return
        self.timer.start(30)

    def update_camera_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def capture_photo(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                filename = "captured_photo.jpg"
                cv2.imwrite(filename, frame)
                self.text_display.append(f"📸 已保存照片为：{filename}")

    def stop_camera_preview(self):
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
