import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False

# 数据展开为4列：每类两个柱子（优化前/后）
categories = ['轻度重叠-优化前', '轻度重叠-优化后', '中度重叠-优化前', '中度重叠-优化后']
values = [65.9, 85.7, 38.4, 65.8]
hatches = ['//', '..', '//', '..']  # 优化前为斜线，优化后为点状

x = np.arange(len(categories))

# 创建图形
fig, ax = plt.subplots(figsize=(8, 4.2))

# 柱状图（黑白填充 + 纹理区分）
bars = ax.bar(x, values, width=0.6, color='white', edgecolor='black', linewidth=1)

# 添加纹理
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)

# 添加顶部数值标签
for i, val in enumerate(values):
    ax.text(i, val + 1.5, f'{val}%', ha='center', va='bottom', fontsize=10)

# 设置横轴标签
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10, rotation=15)

# Y轴与样式
ax.set_ylabel('准确率（%）', fontsize=11)
ax.set_ylim(0, 100)
ax.tick_params(labelsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.3)

# 去除多余边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 布局与保存
plt.tight_layout()
plt.savefig('图9_重叠优化_柱状图_黑白纹理标签版.png', dpi=1200, bbox_inches='tight')
plt.show()
