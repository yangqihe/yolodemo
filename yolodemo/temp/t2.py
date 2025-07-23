import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体和全局样式
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

# 数据
modules = ['基准YOLOv8', '+生物特征模块', '+生物活性识别模块', '+重叠分割优化模块']
accuracies = [84.6, 87.4, 87.9, 92.1]
improvements = [0, 2.8, 0.5, 4.2]


# 方案1：渐变色彩 + 改进幅度标注
def create_gradient_chart():
    fig, ax = plt.subplots(figsize=(12, 7))

    # 使用渐变蓝色，体现递进关系
    colors = ['#8DB4E2', '#5B9BD5', '#2F5597', '#1F3864']

    x = np.arange(len(modules))
    bars = ax.bar(x, accuracies, color=colors, edgecolor='white',
                  linewidth=1.5, alpha=0.9, width=0.6)

    # 添加数值标签
    for i, (bar, acc, imp) in enumerate(zip(bars, accuracies, improvements)):
        height = bar.get_height()
        # 准确率标签
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.3,
                f'{acc:.1f}%', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color='#2F2F2F')

        # 改进幅度标签（除了基准）
        if i > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, height / 2,
                    f'+{imp:.1f}%', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='white',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='red', alpha=0.8))

    # 坐标轴设置
    ax.set_xticks(x)
    ax.set_xticklabels(modules, fontsize=11, ha='center')
    ax.set_ylabel('计数准确率 (%)', fontsize=13, fontweight='bold', color='#333333')
    ax.set_ylim(82, 95)

    # 美化网格和边框
    ax.grid(axis='y', linestyle='--', alpha=0.4, color='#CCCCCC')
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 添加趋势箭头
    for i in range(len(accuracies) - 1):
        ax.annotate('', xy=(i + 1, accuracies[i + 1] - 1), xytext=(i, accuracies[i] + 1),
                    arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=2, alpha=0.7))

    plt.title('系统整体性能递进提升对比', fontsize=15, fontweight='bold',
              color='#2F2F2F', pad=20)
    plt.tight_layout()
    return fig


# 方案2：双轴图 - 准确率 + 提升幅度
def create_dual_axis_chart():
    fig, ax1 = plt.subplots(figsize=(12, 7))

    x = np.arange(len(modules))

    # 左轴：准确率柱状图
    bars1 = ax1.bar(x, accuracies, color='#4472C4', alpha=0.8,
                    edgecolor='white', linewidth=1.5, width=0.6, label='计数准确率')

    # 添加准确率标签
    for i, (bar, acc) in enumerate(zip(bars1, accuracies)):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 f'{acc:.1f}%', ha='center', va='bottom',
                 fontsize=11, fontweight='bold')

    # 右轴：提升幅度折线图
    ax2 = ax1.twinx()
    line = ax2.plot(x[1:], improvements[1:], color='#E74C3C', marker='o',
                    linewidth=3, markersize=8, label='提升幅度')

    # 添加提升幅度标签
    for i, imp in enumerate(improvements[1:], 1):
        ax2.text(i, imp + 0.2, f'+{imp:.1f}%', ha='center', va='bottom',
                 fontsize=10, fontweight='bold', color='#E74C3C')

    # 坐标轴设置
    ax1.set_xticks(x)
    ax1.set_xticklabels(modules, fontsize=11, rotation=15, ha='right')
    ax1.set_ylabel('计数准确率 (%)', fontsize=12, fontweight='bold', color='#4472C4')
    ax1.set_ylim(82, 95)

    ax2.set_ylabel('性能提升幅度 (%)', fontsize=12, fontweight='bold', color='#E74C3C')
    ax2.set_ylim(0, 5)

    # 美化
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    ax1.set_axisbelow(True)

    # 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    plt.title('系统性能累积提升效果图', fontsize=15, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


# 方案3：水平条形图 + 美化
def create_horizontal_chart():
    fig, ax = plt.subplots(figsize=(12, 8))

    # 反转模块顺序，让最终结果在顶部
    modules_rev = modules[::-1]
    accuracies_rev = accuracies[::-1]
    improvements_rev = improvements[::-1]

    y = np.arange(len(modules_rev))

    # 使用渐变色
    colors = ['#1F3864', '#2F5597', '#5B9BD5', '#8DB4E2']

    bars = ax.barh(y, accuracies_rev, color=colors, edgecolor='white',
                   linewidth=1.5, alpha=0.9, height=0.6)

    # 添加数值标签
    for i, (bar, acc, imp) in enumerate(zip(bars, accuracies_rev, improvements_rev)):
        width = bar.get_width()
        # 准确率标签
        ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{acc:.1f}%', ha='left', va='center',
                fontsize=12, fontweight='bold')

        # 改进幅度标签（除了基准）
        if imp > 0:
            ax.text(width / 2, bar.get_y() + bar.get_height() / 2,
                    f'+{imp:.1f}%', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='white')

    # 坐标轴设置
    ax.set_yticks(y)
    ax.set_yticklabels(modules_rev, fontsize=11)
    ax.set_xlabel('计数准确率 (%)', fontsize=13, fontweight='bold')
    ax.set_xlim(80, 95)

    # 美化
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.title('系统模块累积效果展示', fontsize=15, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


# 生成三种方案
print("正在生成方案1：渐变色彩 + 改进幅度标注...")
fig1 = create_gradient_chart()
plt.savefig('系统性能提升_方案1_渐变色彩.png', dpi=300, bbox_inches='tight')
plt.show()

print("正在生成方案2：双轴图...")
fig2 = create_dual_axis_chart()
plt.savefig('系统性能提升_方案2_双轴图.png', dpi=300, bbox_inches='tight')
plt.show()

print("正在生成方案3：水平条形图...")
fig3 = create_horizontal_chart()
plt.savefig('系统性能提升_方案3_水平图.png', dpi=300, bbox_inches='tight')
plt.show()

print("三种方案已生成完成！")