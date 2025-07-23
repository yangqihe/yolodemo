import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据
modules = ['基准YOLOv8', '+生物特征模块', '+生物活性识别模块', '+重叠分割优化模块']
accuracies = [84.6, 87.4, 87.9, 92.1]

x = np.arange(len(modules))
hatches = ['/', 'x', '.', '//']  # 每个模块不同纹理区分

# 图像设置
fig, ax = plt.subplots(figsize=(8, 4.5))

# 黑白柱状图，使用 hatch 填充
bars = ax.bar(x, accuracies, color='white', edgecolor='black', linewidth=1.0)

# 添加每根柱子的纹理
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)

# 添加柱顶文字标签
for i, bar in enumerate(bars):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            f'{accuracies[i]:.1f}%',
            ha='center', va='bottom',
            fontsize=10)

# 设置横坐标标签
ax.set_xticks(x)
ax.set_xticklabels(modules, rotation=15, ha='right', fontsize=10)

# 设置纵坐标
ax.set_ylabel('计数准确率（%）', fontsize=11)
ax.set_ylim(80, 95)
ax.tick_params(axis='y', labelsize=10)

# 网格线
ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.4)

# 去除上右边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 紧凑布局并保存
plt.tight_layout()
plt.savefig('图14_优化版_黑白纹理版.png', dpi=1200, bbox_inches='tight')
plt.show()
