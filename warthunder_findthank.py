#请注意，您需要将上面的代码中的“tank_classifier.xml”替换为您自己训练的坦克分类器的名称
import cv2
import numpy as np

# 获取屏幕分辨率
screen_size = (1920, 1080)

# 创建VideoCapture对象
cap = cv2.VideoCapture(0)

while True:
    # 读取帧
    ret, frame = cap.read()

    # 将帧调整为屏幕大小
    frame = cv2.resize(frame, screen_size)

    # 在帧上运行分类器
    # 这里假设你已经训练好了一个名为tank_classifier.xml的分类器
    # 如果没有，请参考OpenCV文档中的教程来训练一个分类器
    classifier = cv2.CascadeClassifier('tank_classifier.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tanks = classifier.detectMultiScale(gray)

    # 在帧上框选出分类器检测到的内容
    for (x, y, w, h) in tanks:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 显示帧
    cv2.imshow('frame', frame)

    # 按'q'键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放VideoCapture对象并关闭所有窗口
cap.release()
cv2.destroyAllWindows()




