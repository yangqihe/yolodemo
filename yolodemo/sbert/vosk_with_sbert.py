
import os
import queue
import json
import sounddevice as sd
import pyttsx3
import numpy as np
import joblib
from sentence_transformers import SentenceTransformer
from vosk import Model, KaldiRecognizer
from sklearn.metrics.pairwise import cosine_similarity

from sbert.sbert_const import local_huggingface_path

# 加载 Vosk 中文模型
vosk_model_path = "../model/vosk/vosk-model-cn-0.22"
print("判断文件是否存在")
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError("缺少 Vosk 中文模型，请下载解压后放置在当前目录")

print("🔄 正在加载 Vosk 模型...")
rec = KaldiRecognizer(Model(vosk_model_path), 16000)
print("✅ Vosk 模型加载完成")
q = queue.Queue()

print("🔄 正在加载 SBERT 模型...")
# 加载 SBERT 向量模型和模板索引
sbert_index = joblib.load("sbert_intent/intent_sbert_index.pkl")
#sbert_model = SentenceTransformer(sbert_index["model_name"])
sbert_model = SentenceTransformer(local_huggingface_path, local_files_only=True)
print("✅ SBERT 模型加载完成")
index_vecs = sbert_index["embeddings"]
index_labels = sbert_index["labels"]
index_texts = sbert_index["texts"]

# 控制动作执行模拟（仅打印）
def execute_action(action):
    print(f"🦾 执行动作：{action}")
    engine.say(f"执行 {action}")
    engine.runAndWait()

# 简洁聊天回复
def short_reply(text):
    if "你是谁" in text:
        return "我是语音助手"
    elif "天气" in text:
        return "我不查天气"
    elif "你好" in text:
        return "你好！"
    else:
        return "你说的是：" + text[:10]

# 推理函数
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

# 音频流输入
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# 播报引擎
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

def main():
    print("🎤 启动 Vosk + SBERT 语音意图识别系统...")
    with sd.RawInputStream(device=1, samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        last_partial = ""
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print("\n✅ 最终识别结果：", text)
                    if len(text) == 1:
                        print("💬 太短：", text)
                        return
                    label, score, matched = predict_intent(text)
                    print(f"🎯 识别意图：{label}（置信度：{score:.2f}） ← 匹配：{matched}")
                    if label == "chat":
                        reply = short_reply(text)
                        print("💬 回复：", reply)
                        engine.say(reply)
                        engine.runAndWait()
                    else:
                        execute_action(label)
                    last_partial = ""
            else:
                partial = json.loads(rec.PartialResult())
                ptext = partial.get("partial", "")
                if ptext and ptext != last_partial:
                    print("🕓 临时识别：", ptext)
                    last_partial = ptext

if __name__ == "__main__":
    main()
