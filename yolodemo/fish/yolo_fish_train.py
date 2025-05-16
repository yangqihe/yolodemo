from ultralytics import YOLO
import os
print("当前路径:", os.getcwd())

def main():
    #model = YOLO('../yolov8n.pt')
    model = YOLO('yolov8s.pt')  # s = small，适合中等模型能力
    model.train(
        data='./data/dataset/data.yaml',
        epochs=500,
        imgsz=640
    )

if __name__ == '__main__':
    main()
