import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体（如系统无 SimHei 可替换为 Microsoft YaHei）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(123)  # 保证结果可复现
x = np.arange(1, 51)

# 图1：计数准确率
baseline_acc = np.random.normal(loc=87.4, scale=0.2, size=50)
improved_acc = baseline_acc + np.random.normal(loc=0.5, scale=0.1, size=50)

plt.figure(figsize=(10, 6))
plt.plot(x, baseline_acc, label='生物特征模块', color='blue', marker='o', markersize=4)
plt.plot(x, improved_acc, label='+活性识别模块', color='green', marker='s', markersize=4)
plt.fill_between(x, baseline_acc, improved_acc, color='lightgreen', alpha=0.3, label='性能提升区域')

plt.hlines(np.mean(baseline_acc), xmin=1, xmax=50, colors='blue', linestyles='--', label='生物特征平均值')
plt.hlines(np.mean(improved_acc), xmin=1, xmax=50, colors='green', linestyles='--', label='活性识别平均值')

plt.xlabel('实验组编号')
plt.ylabel('计数准确率（%）')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('计数准确率_对比图.png', dpi=300)
plt.close()

# 图2：死鱼误计率
baseline_miscount = np.random.normal(loc=2.3, scale=0.2, size=50)
improved_miscount = baseline_miscount - np.random.normal(loc=2.1, scale=0.2, size=50)

plt.figure(figsize=(10, 6))
plt.plot(x, baseline_miscount, label='生物特征模块', color='orange', marker='^', markersize=4)
plt.plot(x, improved_miscount, label='+活性识别模块', color='purple', marker='D', markersize=4)
plt.fill_between(x, improved_miscount, baseline_miscount, color='plum', alpha=0.3, label='误计降低区域')

plt.hlines(np.mean(baseline_miscount), xmin=1, xmax=50, colors='orange', linestyles='--', label='误计率基准值')
plt.hlines(np.mean(improved_miscount), xmin=1, xmax=50, colors='purple', linestyles='--', label='优化后误计率')

plt.xlabel('实验组编号')
plt.ylabel('死鱼误计率（%）')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('死鱼误计率_对比图.png', dpi=300)
plt.close()
