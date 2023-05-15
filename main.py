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
import configparser
import argparse

print("starting...")

parser = argparse.ArgumentParser(description='Load configuration from file')
parser.add_argument('-c', '--config', metavar='FILE', help='Path to config file', default='config/default.ini')
# 解析命令行参数
args = parser.parse_args()

config = configparser.ConfigParser()
try:
    config.read(args.config)
except FileNotFoundError:
    print('Config file not found, use default config.')

# 显示摄像头采集画面
showGUI = config.getboolean('DEFAULT', 'showGUI', fallback=True)
# 距离检测参数：脸部宽度占比
distanceThreshold = config.getfloat('DEFAULT', 'distanceThreshold', fallback=0.2)
# 脑袋俯仰角度检测参数：脸型上部和下部的宽度比
angleThreshold = config.getfloat('DEFAULT', 'angleThreshold', fallback=1.1)
# 当不展示画面时，多久检测一次
interval =  config.getfloat('DEFAULT', 'interval', fallback=10)
# 视频画面上文字大小
textScale = config.getfloat('DEFAULT', 'textScale', fallback=0.8)
# 距离过近音效文件
distanceSound = config.get('DEFAULT', 'distanceSound', fallback="res/1.mp3")
# 头过低音效文件
angleSound = config.get('DEFAULT', 'angleSound', fallback="res/2.mp3")
# 脸部左上点位序号
faceTopLeft = config.getint('DEFAULT', 'faceTopLeft', fallback=0)
# 脸部右上点位序号
faceTopRight = config.getint('DEFAULT', 'faceTopRight', fallback=16)
# 脸部中部左侧点位序号
faceMiddleLeft = config.getint('DEFAULT', 'faceMiddleLeft', fallback=3)
# 脸部中部右侧点位序号
faceMiddleRight = config.getint('DEFAULT', 'faceMiddleRight', fallback=13)

print(f"distance threshold: {distanceThreshold}\nangle threshold: {angleThreshold}\ninterval: {interval}")
print(f"distance sound: {distanceSound}\nangle sound: {angleSound}")


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
    playSound(distanceSound)

# 低头
def lowHead():
    playSound(angleSound)

print("open camera... if failed, close this, and try again.")

cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor_path = os.path.join(os.path.dirname(__file__), "res/shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(predictor_path)

print("detecting...")
print("Press Ctrl + C to quit")

while True:
    if not showGUI:
        time.sleep(interval)
        # 当锁屏再解锁后，摄像头可能会被关闭，重新打开
        cap = cv2.VideoCapture(0)

    ret, frame = cap.read()
    if not ret:
        continue

    if not showGUI:
        # 先释放摄像头
        cap.release()

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
        faceWitdhTop = landmarks.part(faceTopRight).x - landmarks.part(faceTopLeft).x
        # 脸的中部分宽度
        faceWitdhBottom = landmarks.part(faceMiddleRight).x - landmarks.part(faceMiddleLeft).x
        faceAngle = faceWitdhTop / faceWitdhBottom
        faceWidthPercent = faceWitdhTop / frame_width

        if faceAngle > angleThreshold:
            lowHead()
        if faceWidthPercent > distanceThreshold:
            tooClose()

        # 是否显示画面
        if showGUI:
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                # 绘制人脸关键点
                if n in [faceTopLeft, faceTopRight, faceMiddleLeft, faceMiddleRight]:
                    cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)
                else:
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                
                # 打印每个点的序号
                if n > 30:
                    cv2.putText(frame, f"{n}", (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
                else:
                    cv2.putText(frame, f"{n}", (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            # BGR格式
            colorGreen = (0, 255, 0)
            colorRed = (0, 0, 255)
            colorBlue = (255, 0, 255)
            cv2.putText(frame, f"Angle current:{faceAngle:.3f} / threshold:{angleThreshold:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, textScale, colorGreen if faceAngle < angleThreshold else colorRed, 1)
            cv2.putText(frame, f"Distance current:{faceWidthPercent:.3f} / threshold:{distanceThreshold:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, textScale, colorGreen if faceWidthPercent < distanceThreshold else colorRed, 1)

            # 显示帮助
            cv2.putText(frame, f"Press A: set angle threshold to current value", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, textScale, colorBlue, 1)
            cv2.putText(frame, f"Press D: set distance threshold to current value", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, textScale, colorBlue, 1)
            cv2.putText(frame, f"Press H: hide this window(work in the background)", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, textScale, colorBlue, 1)
            cv2.putText(frame, f"You may need to quick press a few more times to take effect.", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, textScale, colorBlue, 1)
 

            cv2.imshow('frame', frame)

    # 以当前状态设置阈值
    # 角度
    if cv2.waitKey(1) & 0xFF == ord('a'):
        angleThreshold = faceAngle
        print(f"angle threshold: {angleThreshold}")
    # 距离
    if cv2.waitKey(2) & 0xFF == ord('d'):
        distanceThreshold = faceWidthPercent
        print(f"distance threshold: {distanceThreshold}")

    # 隐藏窗口
    if cv2.waitKey(3) & 0xFF == ord('h'):
        showGUI = False
        cv2.destroyAllWindows()
        print(f"dectect frequence: {interval}s")

    # 直接退出
    if cv2.waitKey(4) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

