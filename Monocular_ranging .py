import ctypes
import multiprocessing
import time
from multiprocessing import Process
import cv2
import pynput
from pynput.mouse import Button
from pynput.keyboard import Key, Listener
from win32gui import FindWindow, SetWindowPos, GetWindowText, GetForegroundWindow
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE
import winsound
from simple_pid import PID
import numpy as np
from PIL import Image, ImageGrab
import argparse
import mss


foc = 1990.0        # 镜头焦距
real_hight_person = 66.9   # 行人高度
detect_distance_car = 57.08      # 轿车高度

# 自定义函数，单目测距
def detect_distance_person(h):
    dis_inch = (real_hight_person * foc) / (h - 2)
    dis_cm = dis_inch * 2.54
    dis_cm = int(dis_cm)
    dis_m = dis_cm / 100
    return dis_m

# 自定义函数，改变显示图片大小
def cv_show(p, im0):
    height, width = im0.shape[:2]
    a = 1200 / width  # 宽为1200，计算比例
    size = (1200, int(height * a))
    img_resize = cv2.resize(im0, size, interpolation=cv2.INTER_AREA)
    cv2.imshow(p, img_resize)
    cv2.waitKey(1)  # 1 millisecond

# 自定义函数，绘制带标签的框
def plot_one_box(x, img, color=None, label=None, line_thickness=3, name=None):
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))  # 传过来的x包含有框的两个对角坐标
    h = int(x[3]) - int(x[1])  # 框的高
    dis_m = 1.00
    if name == 'person':  # 根据标签名称调用不同函数计算距离
        dis_m = detect_distance_person(h)
    elif name == 'car':
        dis_m = detect_distance_car(h)
    label += f'  {dis_m}m'  # 在标签后追加距离
    cv2.rectangle(img, c1, c2, color, thickness=line_thickness, lineType=cv2.LINE_AA)
    tf = max(line_thickness - 1, 1)  # font thickness
    t_size = cv2.getTextSize(label, 0, fontScale=line_thickness / 3, thickness=tf)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
    cv2.putText(img, label, (c1[0], c1[1] - 2), 0, line_thickness / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

# 解析命令行参数
parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('--nosave', action='store_false', help='do not save images/videos')
args = parser.parse_args()


ads = 'ads'
pidc = 'pidc'
size = 'size'
stop = 'stop'
lock = 'lock'
show = 'show'
head = 'head'
left = 'left'
title = 'title'
debug = 'debug'
region = 'region'
center = 'center'
radius = 'radius'
weights = 'weights'
classes = 'classes'
confidence = 'confidence'

init = {
    title: ' ',  # 可在后台运行 print(GetWindowText(GetForegroundWindow())) 来检测前台游戏窗体标题
    weights: 'yolov5s.pt',      #我还没训练，训练好了可再转为.engine #weights: '你训练的.engine'
    classes: 0,  # 要检测的标签的序号(标签序号从0开始), 多个时如右 [0, 1] #0是检测person，1是检测tank详情见date/coco128.yaml
    confidence: 0.5,  # 置信度, 低于该值的认为是干扰
    size: 500,  # 截图的尺寸, 屏幕中心 size*size 大小
    radius: 160,  # 瞄准生效半径, 目标瞄点出现在以准星为圆心该值为半径的圆的范围内时才会锁定目标
    ads: 1.2,  # 移动倍数, 调整方式: 瞄准目标旁边并按住 Shift 键, 当准星移动到目标点的过程, 稳定精准快速不振荡时, 就找到了合适的 ADS 值
    center: None,  # 屏幕中心点
    region: None,  # 截图范围
    stop: False,  # 退出, End
    lock: True,  # 锁定, Shift, 按左键时不锁(否则扔雷时也会锁)
    show: True,  # 显示, Down
    head: False,  # 瞄头, Up
    pidc: True,  # 是否启用 PID Controller, 还未完善, Right
    left: False,  # 左键锁, Left, 按鼠标左键时锁
    debug: False,  # Debug 模式, 用来调试 PID 值
}


def game():
    return init[title] == GetWindowText(GetForegroundWindow())


def mouse(data):

    def down(x, y, button, pressed):
        if not game():
            return
        if button == Button.left and data[left]:
            data[lock] = pressed

    with pynput.mouse.Listener(on_click=down) as m:
        m.join()


def keyboard(data):

    def press(key):
        if not game():
            return
        if key == Key.shift:
            data[lock] = True

    def release(key):
        if key == Key.end:
            # 结束程序
            data[stop] = True
            winsound.Beep(400, 200)
            return False
        if not game():
            return
        if key == Key.shift:
            data[lock] = False
        elif key == Key.up:
            data[head] = not data[head]
            winsound.Beep(800 if data[head] else 400, 200)
        elif key == Key.down:
            data[show] = not data[show]
            winsound.Beep(800 if data[show] else 400, 200)
        elif key == Key.right:
            data[pidc] = not data[pidc]
            winsound.Beep(800 if data[pidc] else 400, 200)
        elif key == Key.left:
            data[left] = not data[left]
            winsound.Beep(800 if data[left] else 400, 200)
        elif key == Key.page_down:
            data[debug] = not data[debug]
            winsound.Beep(800 if data[debug] else 400, 200)

    with Listener(on_release=release, on_press=press) as k:
        k.join()


def loop(data):

    from toolkit import Capturer, Detector, Timer
    capturer = Capturer(data[title], data[region])
    detector = Detector(data[weights], data[classes])
    winsound.Beep(800, 200)

    try:
        import os
        root = os.path.abspath(os.path.dirname(__file__))
        driver = ctypes.CDLL(f'{root}/logitech.driver.dll')
        ok = driver.device_open() == 1
        if not ok:
            print('初始化失败, 未安装罗技驱动')
    except FileNotFoundError:
        print('初始化失败, 缺少文件')

    def move(x: int, y: int):
        if (x == 0) & (y == 0):
            return
        driver.moveR(x, y, True)

    def inner(point):
        """
        判断该点是否在准星的瞄准范围内
        """
        a, b = data[center]
        x, y = point
        return (x - a) ** 2 + (y - b) ** 2 < data[radius] ** 2

    def follow(aims):
        """
        从 targets 里选目标瞄点距离准星最近的
        """
        if len(aims) == 0:
            return None

        # 瞄点调整
        targets = []
        for index, clazz, conf, sc, gc, sr, gr in aims:
            if conf < data[confidence]:  # 特意把置信度过滤放到这里(便于从图片中查看所有识别到的目标的置信度)
                continue
            _, _, _, height = sr
            sx, sy = sc
            gx, gy = gc
            differ = (height // 7) if data[head] else (height // 3)
            newSc = sx, sy - height // 2 + differ  # 屏幕坐标系下各目标的瞄点坐标, 计算身体和头在方框中的大概位置来获得瞄点, 没有采用头标签的方式(感觉效果特别差)
            newGc = gx, gy - height // 2 + differ
            targets.append((index, clazz, conf, newSc, newGc, sr, gr))
        if len(targets) == 0:
            return None

        # 找到目标
        cx, cy = data[center]
        index = 0
        minimum = 0
        for i, item in enumerate(targets):
            index, clazz, conf, sc, gc, sr, gr = item
            sx, sy = sc
            distance = (sx - cx) ** 2 + (sy - cy) ** 2
            if minimum == 0:
                index = i
                minimum = distance
            else:
                if distance < minimum:
                    index = i
                    minimum = distance
        return targets[index]

    text = 'Realtime Screen Capture Detect'
    pidx = PID(2, 0, 0.02, setpoint=0)

    # 主循环
    while True:
        try:

            if data[stop]:
                break

            # 生产数据
            t1 = time.perf_counter_ns()

            img = Capturer.backup(data[region])  # 如果句柄截图是黑色, 不能正常使用, 可以使用本行的截图方法
            t2 = time.perf_counter_ns()
            aims, img = detector.detect(image=img, show=data[show])  # 目标检测, 得到截图坐标系内识别到的目标和标注好的图片(无需展示图片时img为none)
            t3 = time.perf_counter_ns()
            aims = detector.convert(aims=aims, region=data[region])  # 将截图坐标系转换为屏幕坐标系
            # print(f'{Timer.cost(t3 - t1)}, {Timer.cost(t2 - t1)}, {Timer.cost(t3 - t2)}')

            # 找到目标
            target = follow(aims)

            # 移动准星
            if data[lock] and target:
                index, clazz, conf, sc, gc, sr, gr = target
                if inner(sc):
                    cx, cy = data[center]
                    sx, sy = sc
                    x = sx - cx
                    y = sy - cy
                    box = (sr[0],sr[1],sr[2]+sr[0],sr[3]+sr[1])


                    # 示例代码中的一部分，用于处理框的坐标和标签
                    conf2 = target[2]  # 示例中的置信度值
                    xyxy = box  # 示例中的框坐标
                    label = target[1]  # 示例中的标签
                    cls = target[0]  # 示例中的类别索引
                    colors = [(255, 0, 0)]  # 示例中的颜色列表
                    names = [label]  # 示例中的标签名称列表
                    with mss.mss() as sct:
                        # The screen part to capture
                        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
                        output = "fullscreen.png"

                        # Grab the data
                        sct_img = sct.grab(monitor)

                        # Save to the picture file
                        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                    im0 = cv2.imread('fullscreen.png')  # 示例中的图像
                    if conf2 > 0.4:  # 置信度小于0.4时不显示
                        # person，显示person标签的框，并单独做person的测距
                        if names[int(cls)] == 'person':
                            plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3,
                                         name=names[int(cls)])  # 画框函数

                    if args.nosave:
                        cv_show('image', im0)
                        k = cv2.waitKey(1)  # 0:不自动销毁也不会更新, 1:1ms延迟销毁
                    if k % 256 == 27:
                        cv2.destroyAllWindows()
                        exit('ESC ...')


        except:
            pass


if __name__ == '__main__':
    multiprocessing.freeze_support()
    manager = multiprocessing.Manager()
    data = manager.dict()
    data.update(init)
    # 初始化数据
    from toolkit import Monitor
    data[center] = Monitor.resolution.center()
    c1, c2 = data[center]
    data[region] = c1 - data[size] // 2, c2 - data[size] // 2, data[size], data[size]
    # 创建进程
    pm = Process(target=mouse, args=(data,), name='Mouse')
    pk = Process(target=keyboard, args=(data,), name='Keyboard')
    pl = Process(target=loop, args=(data,), name='Loop')
    # 启动进程
    pm.start()
    pk.start()
    pl.start()
    pk.join()  # 不写 join 的话, 使用 dict 的地方就会报错 conn = self._tls.connection, AttributeError: 'ForkAwareLocal' object has no attribute 'connection'
    pm.terminate()  # 鼠标进程无法主动监听到终止信号, 所以需强制结束
