# import sounddevice as sd
# import soundfile as sf
# import whisper
# import numpy as np
#
# def record_audio(duration=3, samplerate=16000, filename="temp.wav"):
#     print("🎙️ 开始录音 3 秒...")
#     data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
#     sd.wait()
#     sf.write(filename, data, samplerate)
#     print(f"✅ 录音保存为 {filename}")
#     print(f"🎚️ 最大振幅: {np.max(np.abs(data))}")
#     return filename
#
# def recognize_with_whisper(filename):
#     print("🔍 加载 Whisper 模型...")
#     model = whisper.load_model("medium")  # or "small", "medium", "large"
#     print("📥 开始识别...")
#     result = model.transcribe(filename, language="zh")
#     print("📝 识别结果：", result['text'])
#
# if __name__ == "__main__":
#     path = record_audio()
#     recognize_with_whisper(path)


# from sentence_transformers import SentenceTransformer
#
# from sbert.sbert_const import local_model_path
#
# model = SentenceTransformer(
#     local_model_path,
#     local_files_only=True
# )
# print("✅ 本地模型加载成功")


# import whisper
# model = whisper.load_model("medium").to("cuda")
# # True 表示 GPU 可用


import difflib
from pypinyin import lazy_pinyin

# control_templates = {
#     "extend_arm": ["打开机械臂", "伸出机械臂"],
#     "retract_arm": ["收回机械臂", "关闭机械臂"],
#     "open_camera": ["打开相机", "启动摄像头"],
#     # 可继续补充你的指令
# }

# def get_best_pinyin_match(input_text, templates, threshold=0.6):
#     input_pinyin = lazy_pinyin(input_text)
#     best_match = None
#     best_score = 0.0
#
#     for template in templates:
#         template_pinyin = lazy_pinyin(template)
#         matcher = difflib.SequenceMatcher(None, input_pinyin, template_pinyin)
#         score = matcher.ratio()
#         if score > best_score:
#             best_match = template
#             best_score = score
#
#     return (best_match, best_score) if best_score >= threshold else (input_text, best_score)
#
# # 扁平化模板
# all_templates = [phrase for phrases in control_templates.values() for phrase in phrases]
#
# # 测试样例
# inputs = ["打开机械壁", "收回机械币", "打開相機"]
# for text in inputs:
#     corrected, score = get_best_pinyin_match(text, all_templates)
#     print(f"原句: {text} => 纠正: {corrected}（相似度: {score:.2f}）")


import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.backends.cudnn.is_available())