import cv2
import dlib
import datetime
import time
import os
import math
import numpy as np
import tkinter as tk
from playsound import playsound
import _thread

print("starting...")

def playSoundAsync():
    isPlaying = {}
    def inner(file):
        nonlocal isPlaying
        if file not in isPlaying:
            isPlaying[file] = True
            playsound(file)
            del isPlaying[file]
    return inner

sound = playSoundAsync()

# 播放声音
def playSound(file):
    file = os.path.join(os.path.dirname(__file__), file)
    try:
        _thread.start_new_thread(sound, (file, ))
    except:
        print("Error: unable to start thread")

# 太近
def tooClose():
    playSound("res/1.mp3")

# 低头
def lowHead():
    playSound("res/2.mp3")

print("open camera...")

# 显示摄像头采集画面
showGUI = True
# 距离检测参数：脸部宽度占比
distanceThreshold = 0.2
# 脑袋俯仰角度检测参数：脸型上部和下部的宽度比
headThreshold = 1.1

print(f"distance threshold: {distanceThreshold}\nhead angle threshold: {headThreshold}")

cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor_path = os.path.join(os.path.dirname(__file__), "res/shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(predictor_path)

print("detecting...")
print("Press Ctrl + C to quit")

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
        # 脸的上部分宽度
        faceWitdhTop = landmarks.part(16).x - landmarks.part(0).x
        # 脸的中部分宽度
        faceWitdhBottom = landmarks.part(13).x - landmarks.part(3).x
        faceAngle = faceWitdhTop / faceWitdhBottom
        faceWidthPercent = faceWitdhTop / frame_width

        if faceAngle > headThreshold:
            lowHead()
        if faceWidthPercent > distanceThreshold:
            tooClose()

        # 是否显示画面
        if showGUI:
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                # 绘制人脸关键点，红色点
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                # 打印每个点的序号
                cv2.putText(frame, f"{n}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
            # BGR格式
            colorGreen = (0, 255, 0)
            colorRed = (0, 0, 255)
            cv2.putText(frame, f"angle: {faceAngle:.3f} / {headThreshold:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, colorGreen if faceAngle < headThreshold else colorRed, 1)
            cv2.putText(frame, f"distanceq: {faceWidthPercent:.3f} / {distanceThreshold:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, colorGreen if faceWidthPercent < distanceThreshold else colorRed, 1)
            cv2.imshow('frame', frame)

    # 以当前状态设置阈值
    # 角度
    if cv2.waitKey(2) & 0xFF == ord('a'):
        headThreshold = faceAngle
        print(f"head angle threshold: {headThreshold}")
    # 距离
    if cv2.waitKey(2) & 0xFF == ord('d'):
        distanceThreshold = faceWidthPercent
        print(f"distance threshold: {distanceThreshold}")

    # 隐藏窗口
    if cv2.waitKey(2) & 0xFF == ord('h'):
        showGUI = False
        cv2.destroyAllWindows()
    # 直接退出
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

