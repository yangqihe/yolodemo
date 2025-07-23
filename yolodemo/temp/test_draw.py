import cv2
import os

# 图像路径和框坐标路径
IMAGE_PATH = "data/1747104899.jpg"
BOX_FILE = "output/boxes.txt"

# 根据 IMAGE_PATH 构建输出路径（加下划线）
image_dir, image_name = os.path.split(IMAGE_PATH)
name, ext = os.path.splitext(image_name)
OUTPUT_PATH = os.path.join("output", f"{name}_.jpg")

# 读取图像
img = cv2.imread(IMAGE_PATH)

# 读取坐标并画框
with open(BOX_FILE, "r") as f:
    for line in f:
        if len(line.strip()) > 0:
            x1, y1, x2, y2 = map(int, line.strip().split(","))
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

# 保存结果图像
cv2.imwrite(OUTPUT_PATH, img)
print(f"✅ 已重新绘制检测框，保存至：{OUTPUT_PATH}")

# 显示图像窗口
cv2.imshow("Redrawn Bounding Boxes", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
