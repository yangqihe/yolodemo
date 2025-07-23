import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据
modules = ['基准YOLOv8', '+生物特征模块', '+生物活性识别模块', '+重叠分割优化模块']
accuracies = [84.6, 87.4, 87.9, 92.1]

x = np.arange(len(modules))

# 图像设置
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制统一颜色柱状图
bars = ax.bar(x, accuracies, color='cornflowerblue', edgecolor='black', linewidth=1.0)

# 添加柱顶文字标签
for i, bar in enumerate(bars):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            f'{accuracies[i]:.1f}%',
            ha='center', va='bottom',
            fontsize=11, fontweight='bold')

# 设置横坐标标签
ax.set_xticks(x)
ax.set_xticklabels(modules, rotation=15, ha='right', fontsize=11)

# 设置纵坐标
ax.set_ylabel('计数准确率 / %', fontsize=11, fontweight='bold')
ax.set_ylim(80, 95)
ax.tick_params(axis='y', labelsize=11)

# 网格线美化
ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.5)

# 去除上右边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 紧凑布局
plt.tight_layout()

# 保存图像
plt.savefig('图14_优化版统一色调.png', dpi=600)
plt.show()
