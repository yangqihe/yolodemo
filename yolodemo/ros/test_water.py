import cv2

# 读取一张水下图片
#image = cv2.imread('C:\\Users\\qihe\\Desktop\\Captured_Images\\微信图片_20250512155020.png')
image = cv2.imread(r"C:\Users\qihe\Desktop\Captured_Images\_20250512134221.jpg")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 去噪 + 边缘检测
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)

# 提取轮廓并计数
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
particles = [cnt for cnt in contours if cv2.contourArea(cnt) > 5]

print(f"颗粒物数量: {len(particles)}")

# 可视化结果
for cnt in particles:
    cv2.drawContours(image, [cnt], -1, (0, 255, 0), 2)
cv2.imshow("颗粒检测结果", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
