import matplotlib.pyplot as plt
import numpy as np
import json
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据文件路径
DATA_FILE = 'fixed_data.json'

# 尝试加载已有数据
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data_store = json.load(f)
else:
    data_store = {}

# 用于生成或读取变量的函数
def get_or_generate_array(key, generator_fn):
    if key in data_store:
        return np.array(data_store[key])
    else:
        val = generator_fn()
        data_store[key] = val.tolist()
        return val

# 模拟数据（只在首次缺失时生成）
x = np.arange(1, 51)

baseline = get_or_generate_array("baseline_生物特征", lambda: np.random.normal(loc=84.6, scale=0.3, size=50))
improved = get_or_generate_array("improved_生物特征", lambda: baseline + np.random.normal(loc=2.8, scale=0.3, size=50))

# 将数据存回 JSON 文件
with open(DATA_FILE, 'w') as f:
    json.dump(data_store, f, indent=2)

# 创建图形
fig, ax = plt.subplots(figsize=(6.5, 4.2))

# 绘制曲线（黑白线型区分，适合打印）
ax.plot(x, baseline, linestyle='-', color='black', marker='o', markersize=3, label='基准 YOLOv8')
ax.plot(x, improved, linestyle='--', color='black', marker='s', markersize=3, label='引入生物特征模块')

# 平均线
ax.axhline(np.mean(baseline), linestyle=':', color='black', linewidth=1, label='基准平均值')
ax.axhline(np.mean(improved), linestyle='-.', color='black', linewidth=1, label='优化后平均值')

# 坐标轴
ax.set_xlabel('实验组编号', fontsize=11)
ax.set_ylabel('计数准确率（%）', fontsize=11)
ax.set_xlim(1, 50)
ax.set_ylim(83, 89)
ax.tick_params(labelsize=10)

# 图例统一放底部
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels,
           loc='lower center', bbox_to_anchor=(0.5, -0.05),
           ncol=4, fontsize=10, frameon=False)

# 去除多余边框和背景
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(False)

# 紧凑布局并保存
plt.tight_layout()
plt.subplots_adjust(bottom=0.15)
plt.savefig('图_生物特征模块_精简黑白版.png', dpi=1200, bbox_inches='tight')
plt.show()
