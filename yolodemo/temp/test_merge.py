import cv2
import os
from ultralytics import YOLO

# 路径配置
MODEL_PATH = "best.pt"
IMAGE_PATH = "data/1747104889.jpg"
BOX_FILE = "output/boxes.txt"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 输出路径
filename = os.path.basename(IMAGE_PATH)
basename, ext = os.path.splitext(filename)
output_image = os.path.join(OUTPUT_FOLDER, f"{basename}_final{ext}")

# 加载模型
model = YOLO(MODEL_PATH)
img = cv2.imread(IMAGE_PATH)

# 推理阶段获取第一组坐标
results = model.predict(img, conf=0.4, iou=0.5, device="0", classes=[0], verbose=False)
model_coords = []
if results[0].boxes and results[0].boxes.xyxy is not None:
    for box in results[0].boxes.xyxy.cpu().numpy():
        x1, y1, x2, y2 = map(int, box[:4])
        model_coords.append((x1, y1, x2, y2))

# 从文件中读取第二组坐标
file_coords = []
# if os.path.exists(BOX_FILE):
#     with open(BOX_FILE, "r") as f:
#         for line in f:
#             try:
#                 x1, y1, x2, y2 = map(int, line.strip().split(","))
#                 file_coords.append((x1, y1, x2, y2))
#             except:
#                 continue  # 跳过格式错误行

# 合并两组坐标并去重
all_coords = list(set(model_coords + file_coords))  # 合并并去重

# 绘制所有框
for x1, y1, x2, y2 in all_coords:
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

# 保存图像
cv2.imwrite(output_image, img)
print(f"✅ 图像保存至: {output_image}")
print(f"📦 坐标文件: {BOX_FILE}")
print(f"🐟 总绘制框数（去重后）: {len(all_coords)}")

# 显示图像
cv2.imshow("Final Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
