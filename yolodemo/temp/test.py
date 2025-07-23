import cv2
import time
import glob
import os
from ultralytics import YOLO

# 配置路径
MODEL_PATH = "best.pt"
IMAGE_FOLDER = "data"
OUTPUT_FOLDER = "output1"

# MODEL_PATH = "model/best_250s.pt"
# IMAGE_FOLDER = "data"
# OUTPUT_FOLDER = "output4"

# 创建输出目录
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 加载 YOLO 模型
model = YOLO(MODEL_PATH)

# 加载图像路径
image_paths = sorted(glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg")))

# 保存检测结果 (filename, count)
results_summary = []

# 遍历检测
for img_path in image_paths:
    filename = os.path.basename(img_path)
    frame = cv2.imread(img_path)

    # YOLO 推理
    results = model.predict(
        frame,
        conf=0.4,
        iou=0.5,
        device="0",        # 如无 GPU 改为 "cpu"
        classes=[0],       # 只检测鱼类（class 0）
        verbose=False
    )

    # 拿到检测框数据
    boxes = results[0].boxes
    fish_count = 0
    if boxes is not None and boxes.xyxy is not None:
        box_array = boxes.xyxy.cpu().numpy()
        fish_count = len(box_array)  # 目标数量
        for box in box_array:
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # 保存图像
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    cv2.imwrite(output_path, frame)

    # 记录到结果列表
    results_summary.append((filename, fish_count))

cv2.destroyAllWindows()

# 按鱼的数量降序排序并打印
#results_summary.sort(key=lambda x: x[1], reverse=True)

print("\n📊 检测结果（按鱼数量降序）:")
for fname, count in results_summary:
    print(f"📷 {fname} - 检测到鱼数量: {count}")

print("✅ 所有图像处理与保存完成")
