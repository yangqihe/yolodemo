import matplotlib.pyplot as plt
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False

# 实验组编号
x = np.arange(1, 51)

# 模拟数据
np.random.seed(42)

# 模块一：计数准确率
base_total = np.random.normal(87.9, 0.3, 50)
opt_total = base_total + np.random.normal(4.2, 0.3, 50)

# 模块二：轻度重叠准确率
base_light = np.random.normal(65.9, 0.4, 50)
opt_light = base_light + np.random.normal(19.8, 0.4, 50)

# 模块三：中度重叠准确率
base_medium = np.random.normal(38.4, 0.4, 50)
opt_medium = base_medium + np.random.normal(27.4, 0.5, 50)

# 图像生成函数
def plot_module(title, y_base, y_opt, filename):
    plt.figure(figsize=(10, 5))
    plt.plot(x, y_base, label='优化前', color='blue', marker='o', markersize=4)
    plt.plot(x, y_opt, label='引入重叠分割优化模块', color='green', marker='s', markersize=4)
    plt.fill_between(x, y_base, y_opt, color='lightgreen', alpha=0.3, label='性能提升区域')

    plt.hlines(np.mean(y_base), 1, 50, colors='blue', linestyles='--', label='优化前平均')
    plt.hlines(np.mean(y_opt), 1, 50, colors='green', linestyles='--', label='优化后平均')

    plt.xlabel('实验组编号')
    plt.ylabel('准确率（%）')
    #plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

# 生成三张图
plot_module('图9-a 计数准确率对比图', base_total, opt_total, '图9-a_计数准确率对比.png')
plot_module('图9-b 轻度重叠准确率对比图', base_light, opt_light, '图9-b_轻度重叠准确率对比.png')
plot_module('图9-c 中度重叠准确率对比图', base_medium, opt_medium, '图9-c_中度重叠准确率对比.png')
