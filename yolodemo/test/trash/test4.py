import joblib

# 加载模型和向量器
vectorizer = joblib.load("intent_model/vectorizer.pkl")
classifier = joblib.load("intent_model/intent_classifier.pkl")

def classify_intent(text):
    vec = vectorizer.transform([text])
    label = classifier.predict(vec)[0]
    return label

# 示例
text = "抓一下那个物体"
label = classify_intent(text)
print("意图分类结果：", label)
