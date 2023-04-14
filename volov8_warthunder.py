import win32api
import win32con
import win32gui
import numpy as np
from PIL import ImageGrab
from yolov8 import Detector
import cv2


# 加载模型
detector = Detector('path/to/model')

while True:
    # 获取窗口句柄
    hwnd = 1772448

    # 获取窗口截图
    img = np.array(ImageGrab.grab(bbox=win32gui.GetWindowRect(hwnd)))

    # 对图像进行检测
    results = detector.detect(img)

    # 在屏幕上显示检测结果
    for result in results:
        if result['label'] == 'tank':    #thank可改为识别的东西
            # 计算物体中心点坐标
            x = (result['left'] + result['right']) // 2
            y = (result['top'] + result['bottom']) // 2

            # 移动鼠标到物体中心点位置
            win32api.SetCursorPos((x, y))

            # 点击鼠标左键
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

        cv2.rectangle(img, (result['left'], result['top']), (result['right'], result['bottom']), (0, 255, 0), 2)
        cv2.putText(img, result['label'], (result['left'], result['top'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    (36, 255, 12), 2)

    # 显示图像
    cv2.imshow('window', img)

    # 按下q键退出循环
    if cv2.waitKey(1) == ord('q'):
        break

# 清理资源
cv2.destroyAllWindows()


