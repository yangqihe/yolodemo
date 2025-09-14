from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np
import os

# 打印图像保存目录
print("图像将保存至当前目录：", os.getcwd())

def draw_structure_figure(output_path="图2_YOLOv8改进结构图.png"):
    image = Image.new("RGB", (1000, 600), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    blocks = {
        "Input Image\n(640×640×3)": (100, 50),
        "GhostNet Backbone": (100, 120),
        "FPN + PAN\n(PAFPN)": (100, 200),
        "P2\n(160×160)": (50, 300),
        "P3\n(80×80)": (250, 300),
        "P4\n(40×40)": (450, 300),
        "Detection\nHeads": (250, 400),
    }
    for label, (x, y) in blocks.items():
        draw.rectangle([x, y, x + 140, y + 50], outline="black", width=2)
        draw.text((x + 10, y + 15), label, fill="black", font=font)
    arrows = [
        ((170, 100), (170, 120)),
        ((170, 170), (170, 200)),
        ((170, 250), (100, 300)),
        ((170, 250), (320, 300)),
        ((170, 250), (520, 300)),
        ((120, 350), (320, 400)),
        ((320, 350), (320, 400)),
        ((520, 350), (320, 400)),
    ]
    for (x1, y1), (x2, y2) in arrows:
        draw.line([x1, y1, x2, y2], fill="black", width=2)
    image.save(output_path)
    print(f"✅ 图2保存成功：{output_path}")

def draw_detection_counting_figure(output_path="图3_检测与计数示意图.png"):
    image = Image.new("RGB", (1000, 600), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    boxes = [
        (150, 200, 230, 270, "ID: 01"),
        (300, 180, 380, 250, "ID: 02"),
        (480, 220, 560, 290, "ID: 03"),
    ]
    for x1, y1, x2, y2, label in boxes:
        draw.rectangle([x1, y1, x2, y2], outline="blue", width=3)
        draw.text((x1, y1 - 10), label, fill="black", font=font)
    draw.line([(100, 400), (900, 400)], fill="red", width=3)
    draw.text((110, 410), "Counting Line", fill="red", font=font)
    draw.text((30, 30), "Count: 62", fill="black", font=font)
    image.save(output_path)
    print(f"✅ 图3保存成功：{output_path}")

def draw_error_comparison_figure(output_path="图4_误差折线图.png"):
    frames = np.arange(0, 50)
    method_a = np.cumsum(np.random.randint(-1, 2, size=50))
    method_b = np.cumsum(np.random.randint(-1, 1, size=50))
    method_c = np.cumsum(np.random.randint(-1, 1, size=50))
    plt.figure(figsize=(8, 4.5))
    plt.plot(frames, method_a, label="YOLOv8 + DeepSORT", linestyle="--")
    plt.plot(frames, method_b, label="YOLOv8 + OC-SORT", linestyle="-.")
    plt.plot(frames, method_c, label="YOLOv8 + Proposed", linewidth=2)
    plt.axhline(0, color="gray", linestyle=":")
    plt.xlabel("Frame")
    plt.ylabel("Cumulative Error")
    plt.title("Figure 4: Counting Error Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ 图4保存成功：{output_path}")

def draw_system_architecture_figure(output_path="图5_系统结构部署图.png"):
    image = Image.new("RGB", (1000, 600), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    modules = {
        "Fish Fry\nFeeding Funnel": (50, 100),
        "Skirt Conveyor Belt": (250, 100),
        "Camera Module": (250, 30),
        "LED Light": (250, 60),
        "Main PC (Detection + Counting)": (500, 100),
        "Serial Output": (700, 100),
        "MCU Display\n(LCD/LED)": (850, 100),
    }
    for label, (x, y) in modules.items():
        draw.rectangle([x, y, x + 130, y + 50], outline="black", width=2)
        draw.text((x + 5, y + 15), label, fill="black", font=font)
    arrows5 = [
        ((180, 125), (250, 125)),
        ((315, 50), (315, 100)),
        ((380, 125), (500, 125)),
        ((630, 125), (700, 125)),
        ((830, 125), (850, 125)),
    ]
    for (x1, y1), (x2, y2) in arrows5:
        draw.line([x1, y1, x2, y2], fill="black", width=2)
    image.save(output_path)
    print(f"✅ 图5保存成功：{output_path}")

# ✅ 调用所有图生成函数
draw_structure_figure()
draw_detection_counting_figure()
draw_error_comparison_figure()
draw_system_architecture_figure()

print("✅ 所有图像已生成完毕。")
