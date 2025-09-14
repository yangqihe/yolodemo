# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

# 椭圆参数
A_center, B_center = (-0.8, 0), (0.8, 0)
A_a, A_b, B_a, B_b = 2.0, 1.2, 2.0, 1.2

fig, ax = plt.subplots(figsize=(6,4), dpi=150)

# 椭圆 A：反斜杠填充
ellipseA = Ellipse(A_center, 2*A_a, 2*A_b,
                   facecolor='none', edgecolor='black',
                   hatch='/', lw=1.5)
# 椭圆 B：点填充
ellipseB = Ellipse(B_center, 2*B_a, 2*B_b,
                   facecolor='none', edgecolor='black',
                   hatch='.', lw=1.5)

ax.add_patch(ellipseA)
ax.add_patch(ellipseB)

# 标签
ax.text(0, 0, r'$|A \cap B|$', ha='center', va='center', fontsize=12,
        bbox=dict(facecolor='white', edgecolor='none', pad=1.5))

ax.text(-2.2, 1.1, r'$|A|$', fontsize=12)
ax.text( 1.7, 1.1, r'$|B|$', fontsize=12)
ax.text(0, 0, r'$|A \cap B|$', ha='center', va='center', fontsize=12)
ax.text(0, -1.6, r'$OR=\dfrac{|A\cap B|}{\min(|A|,|B|)}\times 100\%$',
        fontsize=13, ha='center')

# 去掉坐标轴
ax.set_xlim(-2.8, 2.8)
ax.set_ylim(-1.6, 1.2)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)

ax.set_facecolor('white')  # 背景白色

plt.tight_layout()
plt.savefig("overlap_ratio_hatch.png", dpi=600)
plt.savefig("overlap_ratio_hatch.pdf")
plt.show()
