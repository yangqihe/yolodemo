import cv2

# === 修改这里 ===
CAMERA_IP   = "169.254.121.10"   # 摄像头 IP
USERNAME    = "admin"           # 用户名
PASSWORD    = ""           # 密码（如果出厂没改过，可能为空）
STREAM_TYPE = "main"            # "main" 主码流, "sub" 子码流

#RTSP_URL = f"rtsp://{USERNAME}:{PASSWORD}@{CAMERA_IP}:554/h264/ch1/{STREAM_TYPE}/av_stream"
RTSP_URL = "rtsp://admin:@169.254.121.10:554/CHO1"

print(f"[INFO] 尝试连接摄像头: {RTSP_URL}")
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print("[ERROR] 无法连接摄像头，请检查 IP/用户名/密码")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("[WARN] 读取失败，正在重试...")
        continue

    cv2.imshow("MCD Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
