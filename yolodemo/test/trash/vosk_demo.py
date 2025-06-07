from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json

model = Model("vosk-model-small-cn-0.22")
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

rec = KaldiRecognizer(model, 16000)

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("开始语音识别，说话吧...")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if text:
                print("✅ 最终识别结果：", text)
        else:
            partial = json.loads(rec.PartialResult())
            if partial.get("partial"):
                print("🕓 临时识别：", partial["partial"])

    # while True:
    #     data = q.get()
    #     if rec.AcceptWaveform(data):
    #         result = json.loads(rec.Result())
    #         print("识别结果：", result.get("text"))
