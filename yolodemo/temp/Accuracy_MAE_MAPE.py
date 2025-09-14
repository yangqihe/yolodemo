# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# ========== 读取 CSV 文件 ==========
csv_path = "蓝月光.csv"
df = pd.read_csv(csv_path)

# 检查列是否存在
required_cols = ["y_true", "y_pred_basic", "y_pred_opt"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"缺少必须的列: {col}")

# ========== 定义指标计算函数 ==========
def mae(y, yhat):
    return np.mean(np.abs(y - yhat))

def mape(y, yhat):
    return 100 * np.mean(np.abs((y - yhat) / y))

def accuracy(y, yhat, tol=0):
    """tol=0 表示严格准确率；tol=1 表示 ±1 容差准确率"""
    return 100 * np.mean(np.abs(y - yhat) <= tol)

# ========== 计算结果 ==========
results = []
for name, col in [("YOLOv8 基础检测", "y_pred_basic"),
                  ("+ 多模块优化", "y_pred_opt")]:
    preds = df[col]
    results.append({
        "处理方式": name,
        "Accuracy_exact(%)": round(accuracy(df["y_true"], preds, tol=0), 2),
        "Accuracy_±1(%)": round(accuracy(df["y_true"], preds, tol=1), 2),
        "MAE": round(mae(df["y_true"], preds), 2),
        "MAPE(%)": round(mape(df["y_true"], preds), 2),
    })

summary = pd.DataFrame(results)
print(summary)

# 可选：保存结果到新的 CSV
summary.to_csv("summary_results.csv", index=False, encoding="utf-8-sig")
