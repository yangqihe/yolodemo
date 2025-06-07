
import os
import queue
import json
import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer

# 初始化模型
model = Model("vosk-model-small-cn-0.22")
rec = KaldiRecognizer(model, 16000)
q = queue.Queue()

# 初始化语音播报引擎
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # 语速
engine.setProperty('volume', 1.0)  # 音量

# 音频输入设备编号
device_id = 1

# 控制关键词与动作映射
intent_map = {
    "回": "move_to_home",
    "抓": "move_to_pick_position",
    "夹": "close_gripper",
    "张开": "open_gripper",
    "放": "move_to_place_position",
    "停止": "stop",
    "挥手": "wave_hand"
}

# 判断是否为控制指令
def is_control_command(text):
    return any(k in text for k in intent_map)

# 匹配指令
def map_to_command(text):
    for k, v in intent_map.items():
        if k in text:
            return v
    return None

# 执行控制命令（模拟）
def execute_command(cmd):
    print(f"🦾 执行指令：{cmd}")
    engine.say(f"正在执行 {cmd}")
    engine.runAndWait()

# 闲聊响应
def chat_response(text):
    if "你好" in text:
        return "你好，我在呢"
    elif "你是谁" in text:
        return "我是你的语音助手"
    elif "天气" in text:
        return "我不知道天气，但我可以控制机械臂"
    else:
        return "我听到了你说：" + text

# 音频回调
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# 主函数
def main():
    print("🎤 开始语音识别，请讲话...")
    with sd.RawInputStream(device=device_id, samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print("✅ 最终识别结果：", text)
                    if is_control_command(text):
                        cmd = map_to_command(text)
                        if cmd:
                            execute_command(cmd)
                        else:
                            print("⚠️ 无法映射控制指令")
                    else:
                        reply = chat_response(text)
                        print("💬 回复：", reply)
                        engine.say(reply)
                        engine.runAndWait()
            else:
                partial = json.loads(rec.PartialResult())
                if partial.get("partial"):
                    print("🕓 临时识别：", partial["partial"], end="\r")

if __name__ == "__main__":
    main()
