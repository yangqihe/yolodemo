import cv2
import os
from ultralytics import YOLO

# 配置路径
#MODEL_PATH = "model/best_50s.pt"
MODEL_PATH = "best.pt"
#IMAGE_PATH = "data/1747104889.jpg"
#IMAGE_PATH = "data/1747104865.jpg"
#IMAGE_PATH = "data/1747104860.jpg"
#IMAGE_PATH = "data/1747104887.jpg"
#IMAGE_PATH = "data/1747104870.jpg"

IMAGE_PATH = "data2/20250912182537676.jpg"

OUTPUT_FOLDER = "output"

# 创建输出目录
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 加载 YOLO 模型
model = YOLO(MODEL_PATH)

# 加载图像
filename = os.path.basename(IMAGE_PATH)
frame = cv2.imread(IMAGE_PATH)

# YOLO 推理
results = model.predict(
    frame,
    conf=0.4,
    iou=0.5,
    device="0",  # 如无 GPU 改为 "cpu"
    classes=[0],  # 只检测鱼类（class 0）
    verbose=False
)

# 拿到检测框数据
boxes = results[0].boxes
fish_count = 0
box_array = []

if boxes is not None and boxes.xyxy is not None:
    box_array = boxes.xyxy.cpu().numpy()
    fish_count = len(box_array)
    print("📌 检测框坐标列表：")
    for i, box in enumerate(box_array):
        x1, y1, x2, y2 = map(int, box[:4])
        print(f"第{i+1}个框: ({x1}, {y1}, {x2}, {y2})")
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

# 保存框坐标到文件
box_file_path = os.path.join(OUTPUT_FOLDER, "boxes.txt")
with open(box_file_path, "w") as f:
    for box in box_array:
        x1, y1, x2, y2 = map(int, box[:4])
        f.write(f"{x1},{y1},{x2},{y2}\n")

# 保存图像
output_path = os.path.join(OUTPUT_FOLDER, filename)
cv2.imwrite(output_path, frame)

# 打印结果
print("\n📊 检测结果：")
print(f"📷 {filename} - 检测到鱼数量: {fish_count}")
print(f"✅ 已保存检测框图像：{output_path}")
print(f"✅ 检测框坐标已保存至：{box_file_path}")
