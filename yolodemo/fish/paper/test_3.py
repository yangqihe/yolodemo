# -*- coding: utf-8 -*-
# 24 小时计数准确率：黑白图 + CSV + 统计（Windows 中文友好）
import os, csv, numpy as np, matplotlib, matplotlib.pyplot as plt
from matplotlib import font_manager

# === 字体：若无中文字体则自动退回英文，避免乱码 ===
def setup_chinese_font(font_file_path=None):
    cn_candidates = ["Microsoft YaHei", "SimHei", "PingFang SC",
                     "Source Han Sans SC", "Noto Sans CJK SC"]
    fams = {f.name.lower() for f in font_manager.fontManager.ttflist}
    for name in cn_candidates:
        if name.lower() in fams:
            matplotlib.rcParams['font.sans-serif'] = [name, 'DejaVu Sans']
            matplotlib.rcParams['axes.unicode_minus'] = False
            return True
    if font_file_path and os.path.exists(font_file_path):
        font_manager.fontManager.addfont(font_file_path)
        prop = font_manager.FontProperties(fname=font_file_path)
        matplotlib.rcParams['font.sans-serif'] = [prop.get_name(), 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        return True
    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    return False

USE_CN = setup_chinese_font()  # 如需强制中文，可在此传入本地中文字体路径

# === 将数组替换为真实 24 小时准确率（百分数） ===
acc = np.array([
    91.1, 93.4, 94.1, 91.8, 91.2, 92.6, 90.3, 90.2,
    92.5, 94.2, 93.1, 91.9, 92.8, 91.5, 90.1, 93.1,
    94.3, 95.2, 90.1, 90.8, 90.3, 91.9, 92.5, 91.6
], dtype=float)

# === 基本统计 ===
mean = float(acc.mean())
std  = float(acc.std(ddof=1))     # 样本标准差
_min, _max = float(acc.min()), float(acc.max())
cv = std / mean * 100.0           # 变异系数(%)

print(f"Mean={mean:.2f}%, Std={std:.2f}pp, Min={_min:.1f}%, Max={_max:.1f}%, CV={cv:.2f}%")

# === 导出 CSV（UTF-8-SIG，Excel 友好） ===
outbase = "accuracy_24h"
with open(f"{outbase}.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["hour","accuracy_percent"])
    for i, v in enumerate(acc, start=1): w.writerow([i, f"{v:.3f}"])

# === 画图（黑白风格） ===
hours = np.arange(1, 25)
plt.figure(figsize=(7, 3.8))
plt.plot(hours, acc, color='black', lw=1.8, marker='o', markersize=3, label=("逐小时准确率" if USE_CN else "Hourly accuracy"))
plt.axhline(mean, color='0.4', lw=1.2, linestyle=':', label=(f"均值 {mean:.2f}%" if USE_CN else f"Mean {mean:.2f}%"))

plt.xlim(1, 24); plt.ylim(max(0, acc.min()-1.5), min(100, acc.max()+1.5))
plt.xticks([1,4,8,12,16,20,24])

if USE_CN:
    plt.xlabel("时间（小时）"); plt.ylabel("计数准确率（%）")
    #plt.title("24 小时测试期间逐小时计数准确率")
else:
    plt.xlabel("Time (hour)"); plt.ylabel("Counting accuracy (%)")
    plt.title("Hourly counting accuracy over 24-hour test")

plt.legend(frameon=False, loc="lower right")
plt.grid(True, color='0.85', linewidth=0.8)
plt.tight_layout()
plt.savefig(f"{outbase}.png", dpi=600)
plt.savefig(f"{outbase}.pdf")      # 矢量
plt.savefig(f"{outbase}.tiff", dpi=300)
plt.show()
