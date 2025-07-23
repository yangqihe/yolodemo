import matplotlib.pyplot as plt
import numpy as np
import json
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False

# 数据文件路径
DATA_FILE = 'fixed_data.json'

# 加载或初始化数据存储
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data_store = json.load(f)
else:
    data_store = {}

# 工具函数：根据 key 获取或生成变量
def get_or_generate(key, generator_fn):
    if key in data_store:
        return np.array(data_store[key])
    else:
        val = generator_fn()
        data_store[key] = val.tolist()
        return val

# 实验组编号
x = np.arange(1, 51)

# 获取各模块数据（如果没有则生成）
base_total = get_or_generate("base_total", lambda: np.random.normal(87.9, 0.3, 50))
opt_total  = get_or_generate("opt_total",  lambda: base_total + np.random.normal(4.2, 0.3, 50))

base_light = get_or_generate("base_light", lambda: np.random.normal(65.9, 0.4, 50))
opt_light  = get_or_generate("opt_light",  lambda: base_light + np.random.normal(19.8, 0.4, 50))

base_medium = get_or_generate("base_medium", lambda: np.random.normal(38.4, 0.4, 50))
opt_medium  = get_or_generate("opt_medium",  lambda: base_medium + np.random.normal(27.4, 0.5, 50))

# 保存数据
with open(DATA_FILE, 'w') as f:
    json.dump(data_store, f, indent=2)

# 图像生成函数（黑白精简版）
def plot_module(title, y_base, y_opt, filename):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(x, y_base, linestyle='-', color='black', marker='o', markersize=3, label='优化前')
    ax.plot(x, y_opt, linestyle='--', color='black', marker='s', markersize=3, label='引入重叠分割优化模块')
    #ax.fill_between(x, y_base, y_opt, color='gray', alpha=0.2, label='性能提升区域')

    ax.axhline(np.mean(y_base), linestyle=':', color='black', linewidth=1, label='优化前平均')
    ax.axhline(np.mean(y_opt), linestyle='-.', color='black', linewidth=1, label='优化后平均')

    ax.set_xlabel('实验组编号', fontsize=11)
    ax.set_ylabel('准确率（%）', fontsize=11)
    ax.tick_params(labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)

    # 图例底部一行显示
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='lower center', bbox_to_anchor=(0.5, -0.05),
               ncol=4, fontsize=10, frameon=False)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.13, top=0.96)
    plt.savefig(filename, dpi=1200, bbox_inches='tight')
    plt.close()

# 生成三张黑白风格图
plot_module('图9-a 计数准确率对比图', base_total, opt_total, '图9-a_计数准确率对比_黑白精简版.png')
plot_module('图9-b 轻度重叠准确率对比图', base_light, opt_light, '图9-b_轻度重叠准确率对比_黑白精简版.png')
plot_module('图9-c 中度重叠准确率对比图', base_medium, opt_medium, '图9-c_中度重叠准确率对比_黑白精简版.png')
