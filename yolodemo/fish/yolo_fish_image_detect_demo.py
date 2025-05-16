from ultralytics import YOLO
import cv2

# 加载模型
model = YOLO('model/best_250s.pt')  # 替换为你的模型路径

# 读取图像
image_path = 'test/test_small2.jpg'
image = cv2.imread(image_path)

# 推理
results = model(image)

# 解析结果
for result in results:
    boxes = result.boxes
    print(f"检测到 {len(boxes)} 个鱼苗")

    # 绘制检测框
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        cls_id = int(box.cls[0])
        label = f"{model.names[cls_id]} {conf:.2f}"

        # 画框与标签
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

# 显示结果图
cv2.imshow("Fish Fry Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
