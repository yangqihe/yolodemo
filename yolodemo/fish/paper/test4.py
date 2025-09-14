# -*- coding: utf-8 -*-
# 计算均值、标准差、变异系数 (CV)

import numpy as np

# ===== 在这里输入你的 24 个准确率数据（百分数） =====
data = [
    91.1, 93.4, 94.1, 91.8, 91.2, 92.6, 90.3, 90.2,
    92.5, 94.2, 93.1, 91.9, 92.8, 91.5, 90.1, 93.1,
    94.3, 95.2, 90.1, 90.8, 90.3, 91.9, 92.5, 91.6
]

# 转成 numpy 数组
arr = np.array(data, dtype=float)

# 计算
mean_val = arr.mean()
std_val = arr.std(ddof=1)              # 样本标准差
cv_val = std_val / mean_val * 100      # 变异系数（%）

# 输出结果
print(f"均值 (Mean): {mean_val:.2f}%")
print(f"标准差 (SD): {std_val:.2f}%")
print(f"变异系数 (CV): {cv_val:.2f}%")
