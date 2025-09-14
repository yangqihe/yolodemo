# -*- coding: utf-8 -*-
# 黑白期刊风格 ROC 曲线（含 AUC 与最优阈值），自动中/英文，CSV 用 UTF-8-SIG
import os, csv, numpy as np, matplotlib, matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# ========== 0) 字体与中文自动检测 ==========
def has_font(font_names):
    from matplotlib import font_manager
    fams = {f.name.lower() for f in font_manager.fontManager.ttflist}
    files = {os.path.basename(f.fname).split('.')[0].lower() for f in font_manager.fontManager.ttflist}
    for n in font_names:
        if (n.lower() in fams) or (n.lower() in files):
            return True
    return False

CN_FONT_CANDIDATES = ["Microsoft YaHei", "SimHei", "PingFang SC",
                      "Source Han Sans SC", "Noto Sans CJK SC"]
USE_CHINESE_LABELS = has_font(CN_FONT_CANDIDATES)

matplotlib.rcParams['figure.facecolor'] = 'white'
matplotlib.rcParams['savefig.facecolor'] = 'white'
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['font.sans-serif'] = (CN_FONT_CANDIDATES + ['DejaVu Sans']) if USE_CHINESE_LABELS else ['DejaVu Sans']

# ========== 1) 可复现“类真实”数据 ==========
RANDOM_SEED = 2025
N_SAMPLES = 1200
POS_RATIO  = 0.60
OUT_BASENAME = "roc_fry_classification_bw"

np.random.seed(RANDOM_SEED)
n_pos = int(N_SAMPLES * POS_RATIO); n_neg = N_SAMPLES - n_pos
y_true = np.array([1]*n_pos + [0]*n_neg)

# 正样本整体高分：Beta 分布 + 轻噪声
scores_pos = np.random.beta(5, 2, size=n_pos); scores_neg = np.random.beta(2, 5, size=n_neg)
scores_pos = np.clip(scores_pos + np.clip(np.random.normal(0, 0.03, n_pos), -0.08, 0.08), 0, 1)
scores_neg = np.clip(scores_neg + np.clip(np.random.normal(0, 0.03, n_neg), -0.08, 0.08), 0, 1)
y_scores = np.concatenate([scores_pos, scores_neg])

# ========== 2) ROC / AUC ==========
fpr, tpr, thr = roc_curve(y_true, y_scores, pos_label=1)
roc_auc = auc(fpr, tpr)
j = tpr - fpr; i_best = int(np.argmax(j))
best_thr, best_fpr, best_tpr = float(thr[i_best]), float(fpr[i_best]), float(tpr[i_best])

# ========== 3) 保存 CSV（UTF-8-SIG）==========
csv_path = f"{OUT_BASENAME}_data.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["y_true", "y_score"])
    for yt, ys in zip(y_true, y_scores): w.writerow([yt, f"{ys:.6f}"])

# ========== 4) 绘图：黑白风格 ==========
plt.figure(figsize=(6, 6))
# 主曲线：黑色实线
plt.plot(fpr, tpr, color='black', lw=2, label=f"AUC = {roc_auc:.3f}")
# 随机线：灰色虚线
plt.plot([0, 1], [0, 1], color='0.6', lw=1.2, linestyle='--',
         label=("随机分类线" if USE_CHINESE_LABELS else "Chance line"))
# 最优阈值点：黑色实心圆
plt.scatter([best_fpr], [best_tpr], s=40, color='black', zorder=3)

# 注释
ann = (f"最优阈值={best_thr:.2f}\nTPR={best_tpr:.2f}, FPR={best_fpr:.2f}"
       if USE_CHINESE_LABELS else
       f"Best thr={best_thr:.2f}\nTPR={best_tpr:.2f}, FPR={best_fpr:.2f}")
plt.annotate(ann, xy=(best_fpr, best_tpr),
             xytext=(min(best_fpr+0.08, 0.80), min(best_tpr-0.10, 0.90)),
             arrowprops=dict(arrowstyle="->", lw=1), fontsize=10)

plt.xlim(0, 1); plt.ylim(0, 1.05)
if USE_CHINESE_LABELS:
    plt.xlabel("假阳性率（FPR）"); plt.ylabel("真阳性率（TPR）")
    plt.title("活体/死体鱼苗判别 ROC 曲线")
else:
    plt.xlabel("False Positive Rate (FPR)"); plt.ylabel("True Positive Rate (TPR)")
    plt.title("ROC Curve for Live/Dead Fry Classification")

plt.legend(loc="lower right", frameon=False)
plt.grid(True, color='0.85', linewidth=0.8)
plt.tight_layout()

# 导出：PNG(600dpi)/PDF/SVG/EPS/TIFF(300dpi)
plt.savefig(f"{OUT_BASENAME}.png", dpi=600)
plt.savefig(f"{OUT_BASENAME}.pdf")
plt.savefig(f"{OUT_BASENAME}.svg")
plt.savefig(f"{OUT_BASENAME}.eps")
plt.savefig(f"{OUT_BASENAME}.tiff", dpi=300)
plt.show()

print("AUC =", round(roc_auc, 4))
print("Best threshold =", round(best_thr, 4), "| TPR =", round(best_tpr, 4), "| FPR =", round(best_fpr, 4))
print("CSV saved to:", os.path.abspath(csv_path))
