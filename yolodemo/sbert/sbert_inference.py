
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 加载向量索引
data = joblib.load("sbert_intent/intent_sbert_index.pkl")
model = SentenceTransformer(data["model_name"])
index_embeddings = data["embeddings"]
index_labels = data["labels"]
index_texts = data["texts"]

def predict_intent(text, threshold=0.6):
    vec = model.encode([text])
    sims = cosine_similarity(vec, index_embeddings)[0]
    best_idx = np.argmax(sims)
    best_score = sims[best_idx]
    best_label = index_labels[best_idx]
    best_text = index_texts[best_idx]
    if best_score < threshold:
        return "chat", best_score, best_text
    return best_label, best_score, best_text

if __name__ == "__main__":
    print("📥 输入一句话，回车后输出最匹配的意图（输入 q 退出）")
    while True:
        inp = input("你说：")
        if inp.strip().lower() in ["q", "exit", "quit"]:
            break
        label, score, matched = predict_intent(inp)
        print(f"🎯 预测意图：{label}（置信度：{score:.2f}） ← 匹配模板：{matched}")
