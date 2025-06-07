
import os
import queue
import json
import re
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# 模型路径
model_path = "vosk-model-small-cn-0.22"
if not os.path.exists(model_path):
    raise FileNotFoundError("请下载中文模型 vosk-model-small-cn-0.22 并放到脚本目录下")

# 初始化
model = Model(model_path)
rec = KaldiRecognizer(model, 16000)
q = queue.Queue()

# 音频输入设备 ID（可根据系统调整）
device_id = 1

# 分句函数
def split_sentences(text):
    sents = re.split(r'(。|！|\!|？|\?)', text)
    results = []
    for i in range(0, len(sents) - 1, 2):
        results.append(sents[i] + sents[i + 1])
    if len(sents) % 2 == 1:
        results.append(sents[-1])
    return results

# 回调函数
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# 主语音识别循环
def run():
    print("🎙️ 语音识别开始，请讲话...")
    with sd.RawInputStream(device=device_id, samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                final_text = result.get("text", "")
                if final_text:
                    print("✅ 最终识别：")
                    for line in split_sentences(final_text):
                        print("➤", line)
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "")
                if partial_text:
                    print("🕓 临时：", partial_text, end="\r")

if __name__ == "__main__":
    run()
