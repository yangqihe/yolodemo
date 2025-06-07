
import os
import queue
import json
import joblib
import sounddevice as sd
import pyttsx3
import numpy as np
from vosk import Model, KaldiRecognizer

# 初始化模型路径
vosk_model_path = "vosk-model-small-cn-0.22"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError("缺少 Vosk 中文模型，请下载后放在同目录")

rec = KaldiRecognizer(Model(vosk_model_path), 16000)
q = queue.Queue()

# 加载意图分类模型
intent_enabled = False
try:
    vectorizer = joblib.load("intent_model/vectorizer.pkl")
    classifier = joblib.load("intent_model/intent_classifier.pkl")
    intent_enabled = True
    print("✅ 成功加载意图识别模型")
except Exception as e:
    print("⚠️ 未加载意图识别模型，默认使用关键词判断")
    print("错误信息：", e)

# 控制动作映射
action_map = {
    "伸出机械臂": "extend_arm",
    "收回机械臂": "retract_arm",
    "伸出传感器": "extend_sensor",
    "收回传感器": "retract_sensor",
    "开始测量溶氧": "start_oxygen",
    "停止测量溶氧": "stop_oxygen",
    "开始测量ph值": "start_ph",
    "停止测量ph值": "stop_ph",
    "打开相机": "open_camera",
    "开始拍照": "take_photo",
    "关闭相机": "close_camera"
}

# 提取控制动作
def extract_command(text):
    for k, v in action_map.items():
        if k in text:
            return v
    return None

# 控制类关键词辅助判断
def contains_control_keyword(text):
    keywords = ["机械臂", "传感器", "溶氧", "ph", "相机", "拍照"]
    return any(k in text.lower() for k in keywords)

# 简洁聊天回应
def short_reply(text):
    if "你是谁" in text:
        return "我是你的助手"
    elif "天气" in text:
        return "我不查天气"
    elif "你好" in text:
        return "你好"
    else:
        return "你说的是：" + text[:10]

# 播报引擎
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# 音频采集
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# 主程序
def main():
    print("🎤 开始语音识别并执行意图分类...")
    print("🎧 正在使用音频设备：", sd.query_devices(1)["name"])
    last_partial = ""

    with sd.RawInputStream(device=1, samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print("\n✅ 最终识别结果：", text)
                    if intent_enabled:
                        vec = vectorizer.transform([text])
                        proba = classifier.predict_proba(vec)[0]
                        pred = classifier.classes_[np.argmax(proba)]
                        confidence = np.max(proba)

                        print(f"🎯 意图分类：{pred}（置信度：{confidence:.2f}）")

                        # 低置信度 → 强制为 chat
                        if confidence < 0.6:
                            pred = "chat"

                        # ======== 分支结构调整 ========
                        if pred == "chat":
                            reply = short_reply(text)
                            print("💬 回复：", reply)
                            engine.say(reply)
                            engine.runAndWait()
                        elif pred == "control":
                            action = extract_command(text)
                            if action:
                                print("🦾 执行指令：", action)
                                engine.say(f"执行 {action}")
                                engine.runAndWait()
                            elif not contains_control_keyword(text):
                                print("⚠️ 没有控制关键词，转为聊天")
                                reply = short_reply(text)
                                print("💬 回复：", reply)
                                engine.say(reply)
                                engine.runAndWait()
                            else:
                                print("⚠️ 未匹配具体动作，但包含控制关键词")
                    last_partial = ""
            else:
                partial = json.loads(rec.PartialResult())
                ptext = partial.get("partial", "")
                if ptext and ptext != last_partial:
                    print("🕓 临时识别：", ptext)
                    last_partial = ptext

if __name__ == "__main__":
    main()
