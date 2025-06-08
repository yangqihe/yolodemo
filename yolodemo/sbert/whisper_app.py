import sys
import threading
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import pyttsx3
import joblib
import cv2
import whisper

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel, QDesktopWidget
)
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from opencc import OpenCC
import difflib
from pypinyin import lazy_pinyin

from sbert.sbert_const import local_huggingface_path, predict_threshold, control_templates, \
    local_whisper_path, resource_path, intent_to_natural_reply


# ===== 初始化模型变量 =====
model = None
model_loaded = False
model_loading = False
sbert_model = None
sbert_index = None
index_vecs = index_labels = index_texts = []

whisper_model_path = resource_path(local_whisper_path)


def load_model_async(callback=None):
    def load():
        global model, model_loaded, model_loading
        try:
            model = whisper.load_model(whisper_model_path).to("cuda")
            print("✅ 使用 GPU 推理")
        except RuntimeError:
            try:
                model = whisper.load_model(whisper_model_path)
                print("⚠️ 使用 CPU 推理")
            except Exception as e:
                print(f"❌ 模型加载失败: {e}")
                model = None
        model_loaded = model is not None
        model_loading = False
        if callback:
            # ✅ 将 UI 回调安全丢回主线程
            QTimer.singleShot(0, callback)
            #callback()

    global model_loading
    if not model_loading:
        model_loading = True
        threading.Thread(target=load, daemon=True).start()


def load_sbert_index():
    global sbert_model, sbert_index, index_vecs, index_labels, index_texts
    sbert_index = joblib.load(resource_path("sbert/sbert_intent/intent_sbert_index.pkl"))
    sbert_model = SentenceTransformer(local_huggingface_path, local_files_only=True)
    index_vecs = sbert_index["embeddings"]
    index_labels = sbert_index["labels"]
    index_texts = sbert_index["texts"]


def predict_intent(text, threshold=predict_threshold):
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
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.setProperty("volume", 1.0)
    threading.Thread(target=lambda: engine.say(text) or engine.runAndWait(), daemon=True).start()


all_templates = [phrase for phrases in control_templates.values() for phrase in phrases]


class WhisperVoiceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("sbert/img/logo.png")))
        self.setWindowTitle("Whisper 中文语音识别 + 控制执行")
        self.resize(800, 600)
        self.center_window()

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)

        self.status_label = QLabel("⏳ 正在加载模型，请稍候...", self)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: black")

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        self.button = QPushButton("🎙️ 录音识别指令", self)
        self.button.setEnabled(False)
        self.button.clicked.connect(self.start_recognition)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.video_label)
        layout.addWidget(self.text_display)
        layout.addWidget(self.button)
        self.setLayout(layout)

        QTimer.singleShot(1000, lambda: load_model_async(callback=self.enable_button_after_load))
        #load_model_async(callback=self.enable_button_after_load)

    def center_window(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)

    def enable_button_after_load(self):
        if model_loaded:
            self.status_label.setText("✅ 模型加载完成，请开始识别")
            self.button.setEnabled(True)
        else:
            self.status_label.setText("❌ 模型加载失败，请检查路径或配置")
            self.button.setEnabled(False)

    def start_recognition(self):
        if not model_loaded:
            self.status_label.setText("⏳ 模型尚未加载，请稍候...")
            self.button.setEnabled(False)
            load_model_async(callback=self.enable_button_after_load)
            return

        self._start_real_recognition()

    def _start_real_recognition(self):
        self.button.setEnabled(False)
        self.button.setText("🎧 录音中...")
        self.text_display.clear()
        self.status_label.setText("🎤 开始录音...")
        QApplication.processEvents()

        duration = 3
        samplerate = 16000
        audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')

        for i in range(duration, 0, -1):
            self.status_label.setText(f"🎙️ 正在录音（剩余 {i} 秒）...")
            QApplication.processEvents()
            time.sleep(1)

        sd.wait()
        sf.write("temp.wav", audio, samplerate)

        self.status_label.setText("🧠 正在识别中...")
        QApplication.processEvents()

        if not model:
            self.text_display.append("❌ 模型未成功加载，无法识别")
            self.status_label.setText("❌ 模型错误")
            return

        result = model.transcribe("temp.wav", language="zh")
        text = OpenCC('t2s').convert(result['text'].strip())

        self.text_display.append(f"✅ 识别结果：{text}")
        corrected, score = self.get_best_pinyin_match(text, all_templates)
        self.text_display.append(f"原句: {text} => 纠正: {corrected}（相似度: {score:.2f}）")
        text = corrected
        if len(text) > 1:
            label, score, matched = predict_intent(text)
            self.text_display.append(f"📦 指令识别：{label} ({score:.2f})")

            if label == "chat":
                reply = "你说的是：" + text[:10]
            else:
                reply = f"好的，我马上{intent_to_natural_reply.get(label, label)}"
                self.execute_action(label)

            self.text_display.append(f"💬 回复：{reply}")
            speak_async(reply)

        self.status_label.setText("✅ 识别完成")
        self.button.setEnabled(True)
        self.button.setText("🎙️ 录音识别指令")

    def get_best_pinyin_match(self, input_text, templates, threshold=predict_threshold):
        input_pinyin = lazy_pinyin(input_text)
        best_match = None
        best_score = 0.0

        for template in templates:
            template_pinyin = lazy_pinyin(template)
            matcher = difflib.SequenceMatcher(None, input_pinyin, template_pinyin)
            score = matcher.ratio()
            if score > best_score:
                best_match = template
                best_score = score

        return (best_match, best_score) if best_score >= threshold else (input_text, best_score)

    def execute_action(self, label):
        if label == "take_photo":
            QTimer.singleShot(0, self.take_photo_with_camera_check)
        elif label == "open_camera":
            QTimer.singleShot(0, self.show_camera_preview)
        elif label == "close_camera":
            QTimer.singleShot(0, self.stop_camera_preview)

    def update_camera_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0],
                              frame.strides[0], QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def show_camera_preview(self, then_capture=False):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if self.cap.isOpened():
            self.text_display.append("📷 相机已打开")
            self.timer.start(30)
            if then_capture:
                QTimer.singleShot(1500, self.capture_photo)

    def take_photo_with_camera_check(self):
        if not self.cap or not self.cap.isOpened():
            self.show_camera_preview(then_capture=True)
        else:
            self.capture_photo()

    def capture_photo(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                filename = f"photo_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                self.text_display.append(f"📸 已保存照片为：{filename}")

    def stop_camera_preview(self):
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.video_label.clear()
            self.text_display.append("📷 相机已关闭")


if __name__ == '__main__':
    load_sbert_index()  # 启动时加载 SBERT 模型
    app = QApplication(sys.argv)
    win = WhisperVoiceApp()
    win.show()
    sys.exit(app.exec_())
