import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据（轻度 & 中度）
categories = ['轻度重叠', '中度重叠']
before_values = [65.9, 38.4]
after_values = [85.7, 65.8]

x = np.arange(len(categories))
width = 0.35

# 创建较宽矮图形
fig, ax = plt.subplots(figsize=(8, 4.2))  # 宽高比优化

# 绘制柱状图
bars1 = ax.bar(x - width/2, before_values, width, label='优化前',
               color='#FFA07A', edgecolor='black', linewidth=1)
bars2 = ax.bar(x + width/2, after_values, width, label='优化后',
               color='#4CAF50', edgecolor='black', linewidth=1)

# 添加数值标签
for i, (before, after) in enumerate(zip(before_values, after_values)):
    ax.text(i - width/2, before + 1, f'{before}%', ha='center', va='bottom',
            fontsize=10, fontweight='bold')
    ax.text(i + width/2, after + 1, f'{after}%', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

# 坐标轴设置
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=11)
ax.set_ylabel('准确率 (%)', fontsize=12, fontweight='bold')
#ax.set_xlabel('场景类型', fontsize=12, fontweight='bold')
#ax.set_title('重叠分割优化前后准确率对比', fontsize=13, fontweight='bold')
ax.set_ylim(0, 100)
ax.legend(fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.3)

# 去除多余边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 紧凑布局并保存
plt.tight_layout()
plt.savefig('图9_重叠优化对比_紧凑版.png', dpi=600, bbox_inches='tight')
plt.show()
