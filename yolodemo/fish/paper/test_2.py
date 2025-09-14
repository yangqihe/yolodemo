# ---- 字体初始化（放在脚本最前）----
import os, matplotlib
from matplotlib import font_manager

def setup_chinese_font(font_file_path=None):
    """
    优先用系统已有中文字体；如无则尝试加载指定的 TTF 文件；
    仍无，则回退英文（避免乱码）。
    """
    cn_candidates = ["Microsoft YaHei", "SimHei", "PingFang SC",
                     "Source Han Sans SC", "Noto Sans CJK SC"]
    # 1) 系统是否有中文字体
    fams = {f.name.lower() for f in font_manager.fontManager.ttflist}
    for name in cn_candidates:
        if name.lower() in fams:
            matplotlib.rcParams['font.sans-serif'] = [name, 'DejaVu Sans']
            matplotlib.rcParams['axes.unicode_minus'] = False
            return True  # 已启用中文
    # 2) 尝试加载指定 TTF（如果提供）
    if font_file_path and os.path.exists(font_file_path):
        font_manager.fontManager.addfont(font_file_path)
        prop = font_manager.FontProperties(fname=font_file_path)
        matplotlib.rcParams['font.sans-serif'] = [prop.get_name(), 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        return True
    # 3) 回退英文
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    return False

# 用法：
# 1) 如果机器已有中文字体：
setup_chinese_font()


# -*- coding: utf-8 -*-
# 图9：双柱形图（黑白期刊风格）——轻/中度重叠 × 优化前/后
import numpy as np
import matplotlib.pyplot as plt

# ===== 1) 数据：替换为你的真实数值 =====
labels = ['轻度重叠', '中度重叠']   # 横轴分组
vals_before = [65.9, 38.4]          # 优化前准确率（%）
vals_after  = [85.7, 65.8]          # 优化后准确率（%）

# 如有标准差，填入；没有就设为 None（不画误差线）
stderr_before = None  # 例如 [1.2, 1.5]
stderr_after  = None  # 例如 [1.0, 1.3]

# ===== 2) 绘图参数 =====
x = np.arange(len(labels))
width = 0.36

fig, ax = plt.subplots(figsize=(6.2, 4.2))

# 黑白纹理：优化前（斜线），优化后（点状）
bars1 = ax.bar(x - width/2, vals_before, width,
               label='优化前', color='white', edgecolor='black', hatch='//',
               yerr=stderr_before, capsize=3 if stderr_before is not None else 0)
bars2 = ax.bar(x + width/2, vals_after, width,
               label='优化后', color='white', edgecolor='black', hatch='..',
               yerr=stderr_after, capsize=3 if stderr_after is not None else 0)

# 顶部数值标注
for b in list(bars1) + list(bars2):
    h = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, h + max(vals_before+vals_after)*0.02,
            f"{h:.1f}%", ha='center', va='bottom', fontsize=10)

# 坐标轴与样式
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel('准确率（%）')
ax.set_ylim(0, max(vals_before + vals_after) * 1.25)
ax.legend(frameon=False, ncol=2)
ax.grid(axis='y', linestyle='--', linewidth=0.6, color='0.8')

plt.tight_layout()
plt.savefig("figure9_grouped_bar_bw.png", dpi=600)
plt.savefig("figure9_grouped_bar_bw.pdf")
plt.show()
