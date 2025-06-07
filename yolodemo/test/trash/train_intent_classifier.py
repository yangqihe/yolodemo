
import os
import random
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# 控制类语料（可扩展）
control_templates = {
    "伸出机械臂": ["伸出机械臂", "把机械臂伸出来", "展开机械臂", "机械臂前进", "机械臂伸出去"],
    "收回机械臂": ["收回机械臂", "关闭机械臂", "机械臂收回来", "机械臂后退", "机械臂退回去"],
    "伸出传感器": ["伸出传感器", "展开传感器", "把传感器伸出来", "前出传感器", "传感器启动"],
    "收回传感器": ["收回传感器", "关闭传感器", "撤回传感器", "后退传感器", "结束传感器工作"],
    "开始测量溶氧": ["开始测量溶氧", "启动溶氧检测", "检测溶氧", "测氧", "测溶氧"],
    "停止测量溶氧": ["停止测量溶氧", "关闭溶氧", "终止溶氧检测", "取消溶氧", "溶氧检测结束"],
    "开始测量PH值": ["开始测量PH", "检测PH值", "启动PH传感器", "PH值开始检测", "开始PH测量"],
    "停止测量PH值": ["停止测量PH", "终止PH检测", "关闭PH传感器", "结束PH检测", "PH值测完了"],
    "打开相机": ["打开相机", "启动相机", "开启摄像头", "相机工作", "打开摄像"],
    "开始拍照": ["开始拍照", "拍一张", "执行拍摄", "进行拍照", "拍个照片"],
    "关闭相机": ["关闭相机", "关闭摄像头", "停止拍摄", "相机关掉", "结束摄像"]
}

# 聊天语料（更丰富）
chat_examples = [
    "你是谁", "你叫什么", "今天天气好吗", "我们聊聊", "你会干什么", "你真聪明", "再见", "你在干嘛", "讲个笑话",
    "你好", "你喜欢吃什么", "你是机器人吗", "你多大", "你真棒", "你可以说话吗", "你听得到吗", "你叫什么名字",
    "我能问你问题吗", "你几点睡觉", "你喜欢什么颜色", "你喜欢旅行吗", "你喜欢聊天吗", "我们说点别的", "我想问你点事"
]

# 扩展控制类语料（每个表达重复4次）
control_texts = []
for phrases in control_templates.values():
    for p in phrases:
        for _ in range(4):
            control_texts.append(p)

# 扩展聊天语料（每句重复10次）
chat_texts = [s for s in chat_examples for _ in range(10)]

# 合并样本
texts = control_texts + chat_texts
labels = ["control"] * len(control_texts) + ["chat"] * len(chat_texts)

# 打乱顺序
combined = list(zip(texts, labels))
random.shuffle(combined)
texts, labels = zip(*combined)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# 向量化 + 模型训练（设置 max_iter=20000）
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

clf = LogisticRegression(max_iter=20000, solver='lbfgs', class_weight='balanced', random_state=42)
clf.fit(X_train_vec, y_train)

# 模型保存
os.makedirs("intent_model_trained", exist_ok=True)
joblib.dump(clf, "intent_model_trained/intent_classifier.pkl")
joblib.dump(vectorizer, "intent_model_trained/vectorizer.pkl")

# 保存语料
with open("intent_model_trained/train_corpus.txt", "w", encoding="utf-8") as f:
    for text, label in zip(texts, labels):
        f.write(f"{label}\t{text}\n")

# 输出预测报告
y_pred = clf.predict(X_test_vec)
print("📊 分类报告:")
print(classification_report(y_test, y_pred))

# 可视化混淆矩阵
cm = confusion_matrix(y_test, y_pred, labels=["control", "chat"])
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=["control", "chat"], yticklabels=["control", "chat"], cmap="Blues")
plt.title("混淆矩阵")
plt.xlabel("预测")
plt.ylabel("实际")
plt.tight_layout()
plt.savefig("intent_model_trained/confusion_matrix.png")
print("\n✅ 模型训练完成，已保存至 intent_model_trained/")
