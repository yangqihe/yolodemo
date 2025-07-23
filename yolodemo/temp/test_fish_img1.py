import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# 设置中文字体（适用于支持 SimHei 或微软雅黑）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 模拟50组数据
np.random.seed(42)
x = np.arange(1, 51)

# 基准 YOLOv8 准确率：均值 84.6，微小浮动
baseline = np.random.normal(loc=84.6, scale=0.3, size=50)

# 加入生物特征模块后：整体提升 +2.8，微小浮动
improved = baseline + np.random.normal(loc=2.8, scale=0.3, size=50)

# 画图
plt.figure(figsize=(10, 6))
plt.plot(x, baseline, label='基准 YOLOv8', color='blue', marker='o', markersize=4)
plt.plot(x, improved, label='引入生物特征模块', color='red', marker='s', markersize=4)
plt.fill_between(x, baseline, improved, color='pink', alpha=0.3, label='性能提升区域')

# 添加平均线
plt.hlines(np.mean(baseline), xmin=1, xmax=50, colors='blue', linestyles='--', label='基准平均值')
plt.hlines(np.mean(improved), xmin=1, xmax=50, colors='red', linestyles='--', label='优化后平均值')

# 中文标签
#plt.title('引入生物特征模块前后计数准确率对比图（模拟50组实验）')
plt.xlabel('实验组编号')
plt.ylabel('计数准确率（%）')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('准确率对比图.png', dpi=300, bbox_inches='tight')  # 保存图像
plt.show()
