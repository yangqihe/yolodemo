import os
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

from sbert.sbert_const import local_huggingface_path, control_templates

# 加载模型
#model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
model = SentenceTransformer(local_huggingface_path)



# 聊天意图模板
# chat_templates = [
#     "你是谁", "你叫什么名字", "今天天气好吗", "我们聊聊天", "你好", "再见",
#     "你真棒", "你会干什么", "你在干嘛", "你能不能说话"
# ]
chat_templates = [
    # 基础问候
    "你是谁", "你叫什么名字", "你好", "嗨", "早上好", "下午好", "晚上好",
    "再见", "拜拜", "下次见", "很高兴认识你",

    # 功能询问
    "你会干什么", "你有什么功能", "你能帮我什么", "你有什么特长",
    "你会聊天吗", "你能回答问题吗", "你懂多少东西",
    "你是人工智能吗", "你是机器人还是真人",

    # 状态/活动
    "你在干嘛", "你忙吗", "你现在有空吗", "你在线吗",
    "你睡了吗", "你需要休息吗", "你今天工作多久了",

    # 情感/评价
    "你真棒", "你真聪明", "你好可爱", "你太厉害了",
    "我喜欢你", "你让我开心", "你生气了？", "你会难过吗",
    "你有人类情感吗", "你会开玩笑吗",

    # 天气/时间
    "今天天气好吗", "明天会下雨吗", "现在几点了", "今天星期几",
    "今天是几号", "现在是什么季节", "今年是什么年份",

    # 闲聊/开放话题
    "我们聊聊天", "讲个笑话吧", "说个故事听听", "唱首歌好吗",
    "你有爱好吗", "你喜欢什么颜色", "你最爱吃什么",
    "推荐一部电影", "最近有什么新闻", "人生有什么意义",

    # 交互控制
    "你能不能说话", "大声一点", "小声一点", "说慢一点",
    "换个话题吧", "停止说话", "重复一遍", "我没听清",

    # 哲学/技术
    "人类会被AI取代吗", "你怎么看未来", "意识是什么",
    "你怎么学习的", "你的工作原理是什么", "你有记忆吗"
]

# 合并所有模板
texts, labels = [], []
for label, phrases in control_templates.items():
    texts.extend(phrases)
    labels.extend([label] * len(phrases))
texts.extend(chat_templates)
labels.extend(["chat"] * len(chat_templates))

# 编码为向量
embeddings = model.encode(texts)

# 保存索引
os.makedirs("sbert_intent", exist_ok=True)
joblib.dump({
    "texts": texts,
    "labels": labels,
    "embeddings": embeddings,
    "model_name": local_huggingface_path
}, "sbert_intent/intent_sbert_index.pkl")

print("✅ 已构建并保存 SBERT 意图向量索引")
