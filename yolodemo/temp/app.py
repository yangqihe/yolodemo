# import cv2
# import time
# import threading
# from flask import Flask, Response, jsonify
# from ultralytics import YOLO
# from collections import deque
# import numpy as np
#
# app = Flask(__name__)
#
# # ------------------------------
# # 配置参数
# # ------------------------------
# RTSP_URL = "rtsp://admin:@169.254.179.11:554/CHO1"
# MODEL_PATH = "F:/ultralytics-main/runs/train/fish5\weights/best.pt"
#
#
# # ------------------------------
# # 全局状态管理（增加线程锁和轨迹记录）
# # ------------------------------
# class AppState:
#     def __init__(self):
#         self.cap = None
#         self.model = None
#         self.tracked_ids = {}  # 改为字典记录最后出现时间和位置
#         self.total_count = 0
#         self.latest_frame = None
#         self.running = True
#         self.lock = threading.Lock()
#         self.track_history = deque(maxlen=50)  # 轨迹历史记录
#
#
# state = AppState()
#
#
# # ------------------------------
# # 改进的视频处理线程
# # ------------------------------
# def video_processing():
#     # 初始化摄像头
#     state.cap = cv2.VideoCapture(RTSP_URL)
#     state.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#
#     # 加载YOLO模型（增加跟踪参数配置）
#     state.model = YOLO(MODEL_PATH)
#
#     # 指定自定义跟踪器配置文件的路径
#     tracker_config_path = "bytetrack.yaml"  # 替换为实际路径
#
#     while state.running:
#         ret, frame = state.cap.read()
#         if not ret:
#             time.sleep(1)
#             continue
#
#         # 执行目标跟踪（应用自定义参数）
#         results = state.model.track(
#             frame,
#             persist=True,
#             tracker=tracker_config_path,  # 使用配置文件路径
#             conf=0.4,
#             iou=0.5,
#             device="0",
#             verbose=False
#         )
#
#         # 获取当前检测结果
#         if results[0].boxes.id is not None:
#             current_ids = results[0].boxes.id.cpu().numpy().astype(int)
#             boxes = results[0].boxes.xywh.cpu().numpy()
#
#             # 获取当前时间戳
#             current_time = time.time()
#
#             with state.lock:
#                 # 记录轨迹
#                 state.track_history.append((current_time, current_ids, boxes))
#
#                 # 更新计数逻辑
#                 for track_id, box in zip(current_ids, boxes):
#                     # 检查是否为有效新目标
#                     if track_id not in state.tracked_ids:
#                         # 判断是否稳定出现（最近5帧中至少3帧出现）
#                         appear_count = sum(
#                             1 for entry in state.track_history
#                             if track_id in entry[1]
#                         )
#
#                         if appear_count >= 3:
#                             state.tracked_ids[track_id] = {
#                                 'first_seen': current_time,
#                                 'last_seen': current_time,
#                                 'counted': False,
#                                 'positions': [box]
#                             }
#                     else:
#                         # 更新现有目标信息
#                         state.tracked_ids[track_id]['last_seen'] = current_time
#                         state.tracked_ids[track_id]['positions'].append(box)
#
#                         # 检查是否进入计数区域（示例：右侧1/4区域）
#                         x_center = box[0]
#                         if x_center > frame.shape[1] * 0.75 and not state.tracked_ids[track_id]['counted']:
#                             state.total_count += 1
#                             state.tracked_ids[track_id]['counted'] = True
#
#                 # 清理过期目标（超过5秒未出现）
#                 expired_ids = [
#                     tid for tid, data in state.tracked_ids.items()
#                     if current_time - data['last_seen'] > 5
#                 ]
#                 for tid in expired_ids:
#                     del state.tracked_ids[tid]
#
#         # 生成带标注的帧
#         annotated_frame = results[0].plot()
#
#         # 绘制计数区域
#         cv2.rectangle(annotated_frame,
#                       (int(frame.shape[1] * 0.75), 0),
#                       (frame.shape[1], frame.shape[0]),
#                       (0, 255, 255), 2)
#
#         _, jpeg = cv2.imencode('.jpg', annotated_frame)
#         state.latest_frame = jpeg.tobytes()
#
#
# # ------------------------------
# # Flask路由（保持原有）
# # ------------------------------
# @app.route('/')
# def index():
#     return """
#     <html>
#     <head>
#         <title>实时鱼群计数器</title>
#         <style>
#             body { margin: 0; padding: 20px; background: #f0f0f0; }
#             .container { max-width: 1280px; margin: 0 auto; }
#             .video-box { background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
#             #video-feed { width: 100%; height: auto; }
#             .counter {
#                 position: fixed;
#                 top: 20px;
#                 right: 20px;
#                 background: rgba(0,255,0,0.8);
#                 padding: 15px 25px;
#                 border-radius: 8px;
#                 font-family: Arial;
#                 font-size: 24px;
#                 color: #333;
#             }
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="video-box">
#                 <img id="video-feed" src="/video_feed">
#             </div>
#             <div class="counter" id="counter">总鱼数: 加载中...</div>
#         </div>
#         <script>
#             // 自动刷新图像
#             const img = document.getElementById('video-feed');
#             function refreshImage() {
#                 img.src = "/video_feed?" + Date.now();
#             }
#             setInterval(refreshImage, 100);
#
#             // 更新计数器
#             function updateCounter() {
#                 fetch('/count')
#                     .then(response => response.json())
#                     .then(data => {
#                         document.getElementById('counter').innerHTML =
#                             `总鱼数: ${data.count}`;
#                     });
#             }
#             setInterval(updateCounter, 500);
#         </script>
#     </body>
#     </html>
#     """
#
#
# @app.route('/video_feed')
# def video_feed():
#     def generate():
#         while state.running:
#             if state.latest_frame:
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' +
#                        state.latest_frame + b'\r\n')
#             else:
#                 time.sleep(0.1)
#
#     return Response(generate(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
#
#
# @app.route('/count')
# def get_count():
#     return jsonify({"count": state.total_count})
#
# # ...（保持之前的Flask路由不变）...
#
# # ------------------------------
# # 启动和清理
# # ------------------------------
# if __name__ == '__main__':
#     try:
#         thread = threading.Thread(target=video_processing)
#         thread.start()
#         app.run(host='0.0.0.0', port=5000, threaded=True)
#     finally:
#         state.running = False
#         if state.cap:
#             state.cap.release()
#         cv2.destroyAllWindows()
#         print("资源已释放")






import cv2
import time
import threading
from flask import Flask, Response, jsonify
from ultralytics import YOLO
from collections import deque
import numpy as np

app = Flask(__name__)

# ------------------------------
# 配置参数
# ------------------------------
#RTSP_URL = "rtsp://admin:@169.254.179.11:554/CHO1"
RTSP_URL = "rtsp://admin:@169.254.121.10:554/CHO1"
MODEL_PATH = "best.pt"


# ------------------------------
# 全局状态管理（增加线程锁和轨迹记录）
# ------------------------------
class AppState:
    def __init__(self):
        self.cap = None
        self.model = None
        self.tracked_ids = {}  # 改为字典记录最后出现时间和位置
        self.total_count = 0
        self.latest_frame = None
        self.running = True
        self.lock = threading.Lock()
        self.track_history = deque(maxlen=50)  # 轨迹历史记录


state = AppState()


# ------------------------------
# 改进的视频处理线程
# ------------------------------
def video_processing():
    # 初始化摄像头
    state.cap = cv2.VideoCapture(RTSP_URL)
    state.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # 加载YOLO模型（增加跟踪参数配置）
    state.model = YOLO(MODEL_PATH)

    # 指定自定义跟踪器配置文件的路径
    tracker_config_path = "bytetrack.yaml"  # 替换为实际路径

    while state.running:
        ret, frame = state.cap.read()
        if not ret:
            time.sleep(1)
            continue

        # 执行目标跟踪（应用自定义参数）
        # results = state.model.track(
        #     frame,
        #     persist=True,
        #     tracker=tracker_config_path,  # 使用配置文件路径
        #     conf=0.4,
        #     iou=0.5,
        #     device="0",
        #     verbose=False
        # )
        # 在跟踪参数中增加检测稳定性设置（约第109行）
        results = state.model.track(
            frame,
            persist=True,
            tracker=tracker_config_path,
            conf=0.4,
            iou=0.5,
            device="0",
            verbose=False,
            classes=[0],  # 如果只检测鱼类
            show_conf=False  # 隐藏置信度显示
        )
        # 获取当前检测结果
        if results[0].boxes.id is not None:
            current_ids = results[0].boxes.id.cpu().numpy().astype(int)
            boxes = results[0].boxes.xywh.cpu().numpy()

            # 获取当前时间戳
            current_time = time.time()

            with state.lock:
                # 记录轨迹
                state.track_history.append((current_time, current_ids, boxes))

                # 更新计数逻辑
                for track_id, box in zip(current_ids, boxes):
                    # 检查是否为有效新目标
                    if track_id not in state.tracked_ids:
                        # 判断是否稳定出现（最近5帧中至少3帧出现）
                        appear_count = sum(
                            1 for entry in state.track_history
                            if track_id in entry[1]
                        )

                        if appear_count >= 3:
                            state.tracked_ids[track_id] = {
                                'first_seen': current_time,
                                'last_seen': current_time,
                                'counted': False,
                                'positions': [box]
                            }
                    else:
                        # 更新现有目标信息
                        state.tracked_ids[track_id]['last_seen'] = current_time
                        state.tracked_ids[track_id]['positions'].append(box)

                        # 修改为y轴判断
                        y_center = box[1]
                        if y_center > frame.shape[0] * 0.7 and not state.tracked_ids[track_id]['counted']:
                            state.total_count += 1
                            state.tracked_ids[track_id]['counted'] = True

                # 清理过期目标（超过5秒未出现）
                expired_ids = [
                    tid for tid, data in state.tracked_ids.items()
                    if current_time - data['last_seen'] > 5
                ]
                for tid in expired_ids:
                    del state.tracked_ids[tid]

        # 生成带标注的帧
        annotated_frame = results[0].plot()

        # 绘制计数区域
        cv2.rectangle(annotated_frame,
                      (0, int(frame.shape[0] * 0.7)),  # 从底部30%位置开始
                      (frame.shape[1], frame.shape[0]),
                      (0, 255, 255), 2)
        # 在绘制框时添加文字说明（在cv2.rectangle后添加）
        cv2.putText(annotated_frame,
                    "Detection Area",
                    (10, int(frame.shape[0] * 0.7) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 255), 2)
        _, jpeg = cv2.imencode('.jpg', annotated_frame)
        state.latest_frame = jpeg.tobytes()


# ------------------------------
# Flask路由（保持原有）
# ------------------------------
@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>实时鱼群计数器</title>
        <style>
            body { margin: 0; padding: 20px; background: #f0f0f0; }
            .container { max-width: 1280px; margin: 0 auto; }
            .video-box { background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            #video-feed { width: 100%; height: auto; }
            .counter {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0,255,0,0.8);
                padding: 15px 25px;
                border-radius: 8px;
                font-family: Arial;
                font-size: 24px;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="video-box">
                <img id="video-feed" src="/video_feed">
            </div>
            <div class="counter" id="counter">总鱼数: 加载中...</div>
        </div>
        <script>
            // 自动刷新图像
            const img = document.getElementById('video-feed');
            function refreshImage() {
                img.src = "/video_feed?" + Date.now();
            }
            setInterval(refreshImage, 100);

            // 更新计数器
            function updateCounter() {
                fetch('/count')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('counter').innerHTML =
                            `总鱼数: ${data.count}`;
                    });
            }
            setInterval(updateCounter, 500);
        </script>
    </body>
    </html>
    """


@app.route('/video_feed')
def video_feed():
    def generate():
        while state.running:
            if state.latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' +
                       state.latest_frame + b'\r\n')
            else:
                time.sleep(0.1)

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/count')
def get_count():
    return jsonify({"count": state.total_count})

# ...（保持之前的Flask路由不变）...

# ------------------------------
# 启动和清理
# ------------------------------
if __name__ == '__main__':
    try:
        thread = threading.Thread(target=video_processing)
        thread.start()
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        state.running = False
        if state.cap:
            state.cap.release()
        cv2.destroyAllWindows()
        print("资源已释放")