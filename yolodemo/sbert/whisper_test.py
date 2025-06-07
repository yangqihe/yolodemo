import sys
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer


class WhisperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper 中文语音识别")
        self.setGeometry(400, 200, 500, 300)
        self.model = None

        self.init_ui()
        self.load_model_async()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("正在加载 Whisper 模型...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.record_button = QPushButton("🎙️ 开始录音并识别")
        self.record_button.setEnabled(False)
        self.record_button.clicked.connect(self.record_and_recognize)
        layout.addWidget(self.record_button)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def load_model_async(self):
        # 加载模型（异步感知用户）
        QTimer.singleShot(500, self.load_model)

    def load_model(self):
        self.model = whisper.load_model("medium")
        self.status_label.setText("✅ 模型加载完成，可以开始录音")
        self.record_button.setEnabled(True)

    def record_with_countdown(self, duration=3, samplerate=16000, filename="temp.wav"):
        self.status_label.setText(f"🎙️ 正在录音（{duration}秒）...")
        QApplication.processEvents()

        # 开始录音
        audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')

        # 倒计时提示
        for i in range(duration, 0, -1):
            self.status_label.setText(f"🎙️ 正在录音（剩余 {i} 秒）...")
            QApplication.processEvents()
            time.sleep(1)

        # 等待录音完成
        sd.wait()
        sf.write(filename, audio, samplerate)
        max_amp = np.max(np.abs(audio))

        return filename, max_amp

    def record_and_recognize(self):
        self.result_text.setText('')

        self.record_button.setEnabled(False)

        filename, max_amp = self.record_with_countdown()
        self.status_label.setText(f"✅ 录音完成，最大振幅: {max_amp}")
        QApplication.processEvents()

        # 开始识别
        self.status_label.setText("🧠 正在识别中...")
        QApplication.processEvents()

        result = self.model.transcribe(filename, language="zh")
        self.result_text.setText(result['text'])

        self.status_label.setText("✅ 识别完成")
        self.record_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperGUI()
    window.show()
    sys.exit(app.exec_())
