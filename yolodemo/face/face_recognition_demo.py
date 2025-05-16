import face_recognition
import cv2
import os
import numpy as np
import threading
import pyttsx3
import time
from PIL import ImageFont, ImageDraw, Image
import tkinter as tk
from tkinter import Label, Text, Scrollbar, RIGHT, Y, END
from threading import Thread
from PIL import Image, ImageTk
import queue

spoken_names = set()
last_spoken_name = ""
last_spoken_time = 0
speech_queue = queue.Queue()
speaking = threading.Lock()

# 将名字加入语音播报队列
def speak_name(name):
    global last_spoken_name, last_spoken_time
    if name != "未知" and name not in spoken_names:
        spoken_names.add(name)
        last_spoken_name = name
        last_spoken_time = time.time()
        speech_queue.put(name)

# 播报线程（串行语音播报）
def speech_worker():
    while True:
        name = speech_queue.get()
        with speaking:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(name)
            engine.runAndWait()
        speech_queue.task_done()

# 加载已知人脸（支持多图平均编码）
def load_known_faces(folder):
    known_encodings = []
    known_names = []
    for person_name in os.listdir(folder):
        person_folder = os.path.join(folder, person_name)
        if not os.path.isdir(person_folder):
            continue

        encodings = []
        for file in os.listdir(person_folder):
            img_path = os.path.join(person_folder, file)
            if not img_path.lower().endswith(('.jpg', '.png')):
                continue
            img = face_recognition.load_image_file(img_path)
            face_encs = face_recognition.face_encodings(img)
            if face_encs:
                encodings.append(face_encs[0])

        if encodings:
            avg_encoding = np.mean(encodings, axis=0)
            known_encodings.append(avg_encoding)
            known_names.append(person_name)

    return known_encodings, known_names

# 中文文本绘制函数
def draw_chinese_text(frame, text, position, font_path="simhei.ttf", font_size=24, color=(255, 0, 0)):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# 主识别逻辑
class FaceRecognitionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("人脸识别打卡系统")

        # 视频区
        self.video_label = Label(window)
        self.video_label.pack(side="left")

        # 已识别名单显示区
        self.text_box = Text(window, width=30, height=30, font=("Arial", 12))
        self.text_box.pack(side="right", padx=10, pady=10)
        self.scrollbar = Scrollbar(window, command=self.text_box.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text_box.config(yscrollcommand=self.scrollbar.set)

        self.known_encodings, self.known_names = load_known_faces("known_faces")
        self.video = cv2.VideoCapture(1)
        self.frame_count = 0
        self.cached_faces = []

        # 启动语音线程
        threading.Thread(target=speech_worker, daemon=True).start()

        self.update_frame()

    def update_frame(self):
        ret, frame = self.video.read()
        if not ret:
            return

        self.frame_count += 1

        if self.frame_count % 5 == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb_small, model='hog')
            encodings = face_recognition.face_encodings(rgb_small, locations)
            scaled_locations = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in locations]
            self.cached_faces = list(zip(scaled_locations, encodings))

        for (top, right, bottom, left), encoding in self.cached_faces:
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            name = "未知"

            if True in matches:
                match_index = matches.index(True)
                name = self.known_names[match_index]
                if name not in spoken_names:
                    self.text_box.insert(END, f"{name}\n")
                    self.text_box.see(END)
                speak_name(name)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            frame = draw_chinese_text(frame, name, (left, top - 30))

        # 显示正在播报提示
        if time.time() - last_spoken_time <= 2:
            frame = draw_chinese_text(frame, f"正在播报：{last_spoken_name}", (20, 30), font_size=26, color=(255, 255, 255))

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        self.window.after(10, self.update_frame)

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()