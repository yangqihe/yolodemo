
import os
import queue
import json
import joblib
import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer

# 初始化模型路径
vosk_model_path = "vosk-model-small-cn-0.22"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError("缺少 Vosk 中文模型，请下载后放在同目录")

rec = KaldiRecognizer(Model(vosk_model_path), 16000)
q = queue.Queue()

# 加载本地意图分类模型
vectorizer = joblib.load("intent_model/vectorizer.pkl")
classifier = joblib.load("intent_model/intent_classifier.pkl")

def classify_intent(text):
    vec = vectorizer.transform([text])
    return classifier.predict(vec)[0]

# 语音播报引擎初始化
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# 控制动作映射
action_map = {
    "回": "move_to_home",
    "抓": "move_to_pick_position",
    "夹": "close_gripper",
    "张开": "open_gripper",
    "放": "move_to_place_position",
    "停止": "stop",
    "挥手": "wave_hand"
}

# 从文本中抽取控制动作
def extract_command(text):
    for k, v in action_map.items():
        if k in text:
            return v
    return None

# 简短聊天回应
def short_reply(text):
    if "你是谁" in text:
        return "我是你的助手"
    elif "天气" in text:
        return "我不查天气"
    elif "你好" in text:
        return "你好"
    else:
        return "你说的是：" + text[:10]

# 音频流回调
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# 主程序
def main():
    print("🎤 开始语音识别并执行意图分类...")
    last_partial = ""
    with sd.RawInputStream(device=1, samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print("\n✅ 识别文本：", text)
                    intent = classify_intent(text)
                    print("🎯 意图：", intent)

                    if intent == "control":
                        action = extract_command(text)
                        if action:
                            print("🦾 执行指令：", action)
                            engine.say(f"执行 {action}")
                            engine.runAndWait()
                        else:
                            print("⚠️ 未匹配到具体控制动作")
                    elif intent == "chat":
                        reply = short_reply(text)
                        print("💬 回复：", reply)
                        engine.say(reply)
                        engine.runAndWait()

                    last_partial = ""
            else:
                partial = json.loads(rec.PartialResult())
                ptext = partial.get("partial", "")
                if ptext and ptext != last_partial:
                    print("🕓 临时识别：", ptext)
                    last_partial = ptext

if __name__ == "__main__":
    main()
