# 这里是导入依赖，需要这些库
import ctypes
import math
import win32gui
import mss.tools
import torch
from pynput.mouse import Controller
import pyautogui
import numpy as np
import cv2



# 传入两个坐标点，计算直线距离的
class Point:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class Line(Point):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)

    def getlen(self):
        return math.sqrt(math.pow((self.x1 - self.x2), 2) + math.pow((self.y1 - self.y2), 2))

hwnd = win32gui.FindWindow(None, "War Thunder")
# 加载本地模型
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
half = device != 'cpu'
model = torch.hub.load('D:/Users/20064/PycharmProjects/yolov5-02', 'custom',
                       'D:/Users/20064/PycharmProjects/yolov5-02/runs/train/exp4/weights/best.pt',
                       source='local', force_reload=False)
# 定义屏幕宽高
game_width = 1024
game_height = 768

rect = (0, 0, game_width, game_height)
m = mss.mss()
mt = mss.tools

# 加载罗技鼠标驱动，驱动资源来自互联网
driver = ctypes.CDLL('myProjects/logitech.driver.dll')
ok = driver.device_open() == 1
if not ok:
    print('初始化失败, 未安装lgs/ghub驱动')


# 截图保存
def screen_record():
    img = m.grab(rect)
    mt.to_png(img.rgb, img.size, 6, ".png")


# 这边就是开始实时进行游戏窗口推理了
# 无限循环 -> 截取屏幕 -> 推理模型获取到每个敌人坐标 -> 分辨敌我 ->计算每个敌人中心坐标 -> 挑选距离准星最近的敌人 -> 则控制鼠标移动到敌人的身体或者头部
while True:
    # 截取屏幕
    screen_record()
    # 使用模型
    model = model.to(device)
    # 开始推理
    results = model('wtbg.png')

    # 过滤模型
    xmins = results.pandas().xyxy[0]['xmin']
    ymins = results.pandas().xyxy[0]['ymin']
    xmaxs = results.pandas().xyxy[0]['xmax']
    ymaxs = results.pandas().xyxy[0]['ymax']
    class_list = results.pandas().xyxy[0]['class']
    confidences = results.pandas().xyxy[0]['confidence']
    newlist = []
    for xmin, ymin, xmax, ymax, classitem, conf in zip(xmins, ymins, xmaxs, ymaxs, class_list, confidences):
        if classitem == 0 and conf > 0.5:
            newlist.append([int(xmin), int(ymin), int(xmax), int(ymax), conf])
    # 分辨敌我
    if len(newlist) > 0:
        print('newlist:', newlist)

        for teamname in newlist:
            # 当前遍历的人物最高坐标
            ymaxs = int(teamname[3]+50)
            xmaxs = int(teamname[2]+50)


            def cv_show(name, image):
                cv2.imshow(name, image)
                cv2.waitKey(0)
                cv2.destoryAllWindows()


            image = cv2.imread('wtbg.png')
            # 定义矩形坐标
            x, y, w, h = ymaxs, xmaxs, 100, 100

            # 从图像中提取矩形区域
            roi = img[y:y + h, x:x + w]
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([110, 50, 50])
            upper_blue = np.array([130, 255, 255])

            # 定义HSV中粉色的范围
            lower_pink = np.array([140, 150, 0])
            upper_pink = np.array([180, 255, 255])

            # 对HSV图像进行阈值处理，以获取仅蓝色和粉色的颜色
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)

            # 对掩模和原始图像进行按位与操作
            res_blue = cv2.bitwise_and(img, img, mask=mask_blue)
            res_pink = cv2.bitwise_and(img, img, mask=mask_pink)



            # 如果检测到蓝色或粉色，则打印“teammate”
            if (cv2.countNonZero(mask_blue) > 0) or (cv2.countNonZero(mask_pink) > 0):
                print("teammate")

            cv2.waitKey(0)
            cv2.destroyAllWindows()
    elif len(newlist) > 0:
            print('newlist:', newlist)
            # 存放距离数据
            cdList = []
            xyList = []
            for listItem in newlist:    # 循环遍历每个敌人的坐标信息传入距离计算方法获取每个敌人距离鼠标的距离
                # 当前遍历的人物中心坐标
                xindex = int(listItem[2] - (listItem[2] - listItem[0]) / 2)
                yindex = int(listItem[3] - (listItem[3] - listItem[1]) * 2 / 3)
                mouseModal = Controller()
                x, y = mouseModal.position
                L1 = Line(x, y, xindex, yindex)
                print(int(L1.getlen()), x, y, xindex, yindex)
                # 获取到距离并且存放在cdList集合中
                cdList.append(int(L1.getlen()))
                xyList.append([xindex, yindex, x, y])
            # 这里就得到了距离最近的敌人位置了
            minCD = min(cdList)
            # 如果敌人距离鼠标坐标小于150则自动进行瞄准，这里可以改大改小，小的话跟枪会显得自然些
            if minCD < 300:
                for cdItem, xyItem in zip(cdList, xyList):
                    if cdItem == minCD:
                        print(cdItem, xyItem)
                        # 使用驱动移动鼠标
                        driver.moveR(int(xyItem[0] - xyItem[2]),
                                     int(xyItem[1] - xyItem[3]), True)
                        pyautogui.keyDown('shift + x')  # 改为你自己的测距按键，需激光测距+自动装表
                        driver.moveR(int(xyItem[0] - xyItem[2]),
                                     int(xyItem[1] - xyItem[3]), True)
                    break









