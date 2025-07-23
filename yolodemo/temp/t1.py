import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据
categories = ['整体计数', '轻度重叠', '中度重叠']
before_values = [84.6, 65.9, 38.4]
after_values = [92.1, 85.7, 65.8]
improvements = [7.5, 19.8, 27.4]

x = np.arange(len(categories))
width = 0.35

# 创建图形
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左图：优化前后对比
bars1 = ax1.bar(x - width/2, before_values, width, label='优化前',
                color='#ff7f7f', alpha=0.8, edgecolor='white', linewidth=1.2)
bars2 = ax1.bar(x + width/2, after_values, width, label='优化后',
                color='#2ca02c', alpha=0.8, edgecolor='white', linewidth=1.2)

# 添加数值标签
for i, (before, after) in enumerate(zip(before_values, after_values)):
    ax1.text(i - width/2, before + 1, f'{before}%', ha='center', va='bottom', fontweight='bold')
    ax1.text(i + width/2, after + 1, f'{after}%', ha='center', va='bottom', fontweight='bold')

ax1.set_xlabel('场景类型', fontsize=12, fontweight='bold')
ax1.set_ylabel('准确率 (%)', fontsize=12, fontweight='bold')
ax1.set_title('重叠分割优化前后准确率对比', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3)
ax1.set_ylim(0, 100)

# 右图：提升幅度
colors = ['#4472C4', '#70AD47', '#FFC000']
bars3 = ax2.bar(categories, improvements, color=colors, alpha=0.8,
                edgecolor='white', linewidth=1.2)

# 添加数值标签
for i, improvement in enumerate(improvements):
    ax2.text(i, improvement + 0.5, f'+{improvement}%', ha='center', va='bottom',
             fontweight='bold', fontsize=11)

ax2.set_xlabel('场景类型', fontsize=12, fontweight='bold')
ax2.set_ylabel('提升幅度 (%)', fontsize=12, fontweight='bold')
ax2.set_title('各场景准确率提升幅度', fontsize=13, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)
ax2.set_ylim(0, 30)

plt.tight_layout()
plt.savefig('重叠分割综合效果对比.png', dpi=300, bbox_inches='tight')
plt.show()