import cv2
import dlib
import datetime
import time
import os
import math
import numpy as np
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
from pydub import AudioSegment
from pydub.playback import play
import sys

print("starting...")

# 写汉字
def cv2ImgAddText(img, text, pos, textColor=(0, 255, 0), textSize=80):
    if (isinstance(img, np.ndarray)):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontFile = os.path.join(os.path.dirname(__file__), "res/font.ttf")
    fontText = ImageFont.truetype(fontFile, textSize, encoding="utf-8")
    draw.text(pos, text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

# 播放声音
def playSound(file):
    file = os.path.join(os.path.dirname(__file__), file)
    # 读取音频文件
    audio = AudioSegment.from_file(file, format="mp3")
    # 播放音频文件
    sys.stdout = open(os.devnull, "w")
    play(audio)
    sys.stdout = sys.__stdout__


# 太近
def tooClose():
    playSound("res/1.mp3")

# 低头
def lowHead():
    playSound("res/2.mp3")

# 弹出窗口写文字
def show_circle(text):
    # 获取屏幕大小
    root = tk.Tk()
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    root.destroy()

    # 计算窗口大小
    windowWidth = int(screenWidth / 3)
    windowHeight = windowWidth

    # 设置圆的中心坐标和半径
    center = (int(screenWidth/2), int(screenHeight/2))
    radius = int(windowWidth/2)

    # 创建黑色背景
    background = np.zeros((screenHeight, screenWidth, 3), np.uint8)

    # 展示提示文字
    background = cv2ImgAddText(background, text, center)

    # 显示窗口
    cv2.namedWindow("Circle", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
    # 设置窗口属性，不需要焦点
    cv2.moveWindow("Circle", int(screenWidth/2 - windowWidth/2), int(screenHeight/2 - windowHeight/2))
    cv2.resizeWindow("Circle", windowWidth, windowHeight)
    cv2.imshow("Circle", background)
    cv2.waitKey(300)
    cv2.destroyAllWindows()

print("open camera...")

cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor_path = os.path.join(os.path.dirname(__file__), "res/shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(predictor_path)

print("detecting...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # 将图像转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 使用dlib的人脸检测器检测人脸
    faces = detector(gray)

    # 获得整个画面的宽度和高度
    frame_height, frame_width, _ = frame.shape
    
    # 对每个检测到的人脸，进行关键点检测和绘制
    for face in faces:
        landmarks = predictor(gray, face)
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            # 绘制人脸关键点，红色点
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
            # 打印每个点的序号
            cv2.putText(frame, f"{n}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
        width1 = landmarks.part(16).x - landmarks.part(0).x
        width2 = landmarks.part(13).x - landmarks.part(3).x
        # cv2.putText(frame, f"0-16: {width1}", (10, 30), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 1)
        # cv2.putText(frame, f"3-13: {width2}", (10, 60), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 1)
        s = width1 / width2
        cv2.putText(frame, f"1/2: {s}", (10, 90), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 1)

        if s > 1.1:
            lowHead()
            
        s2 = width1 / frame_width
        cv2.putText(frame, f"Percent: {s2}", (10, 120), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 1)
        if s2 > 0.2:
            tooClose()

    # cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

