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
    title: 'War Thunder ',  # 可在后台运行 print(GetWindowText(GetForegroundWindow())) 来检测前台游戏窗体标题
    weights: 'yolov5s.pt',      #我还没训练，训练好了可再转为.engine #weights: '你训练的.engine'
    classes: 0,  # 要检测的标签的序号(标签序号从0开始), 多个时如右 [0, 1] #0是检测person，1是检测tank详情见date/coco128.yaml
    confidence: 0.5,  # 置信度, 低于该值的认为是干扰
    size: 320,  # 截图的尺寸, 屏幕中心 size*size 大小
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
            img = capturer.grab()
            #img = Capturer.backup(data[region])  # 如果句柄截图是黑色, 不能正常使用, 可以使用本行的截图方法
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
                    box = (sr[0],sr[1]-100,sr[2]+sr[0],sr[3]+sr[1])   #检测敌友颜色框大小，sr是离准星最近目标四个点的数据，sr[1]和sr[0]是目标左上角坐标,sr[2]是目标的宽，sr[3]是目标的高
                    print(box)

                    #分别敌我，

                    im = ImageGrab.grab(bbox=(box))
                    im.save('screenshot.png')

                    im = np.array(im)
                    im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

                    lower_green = np.array([34 255, 0])   #你自己设置的小队队友ROG颜色
                    upper_green = np.array([34 255, 0])
                    mask_green = cv2.inRange(im, lower_green, upper_green)

                    lower_blue = np.array([54, 83, 179])     #你自己设置的队友ROG颜色
                    upper_blue = np.array([54, 83, 179])
                    mask_blue = cv2.inRange(im, lower_blue, upper_blue)



                    if data[pidc] and cv2.countNonZero(mask_green) == 0 and cv2.countNonZero(mask_blue) == 0:
                        px = -int(pidx(x))
                        move(px, y)
                    elif cv2.countNonZero(mask_green) == 0 and cv2.countNonZero(mask_blue) == 0:
                        ax = int(x * data[ads])
                        ay = int(y * data[ads])
                        move(ax, ay)


            # 显示检测
            if data[show] and img is not None:
                # 记录耗时
                cv2.putText(img, f'{Timer.cost(t3 - t1)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(img, f'{Timer.cost(t2 - t1)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(img, f'{Timer.cost(t3 - t2)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                # 瞄点划线
                if target:
                    index, clazz, conf, sc, gc, sr, gr = target
                    cv2.circle(img, gc, 2, (0, 0, 0), 2)
                    r = data[size] // 2
                    cv2.line(img, gc, (r, r), (255, 255, 0), 2)
                # 展示图片
                cv2.namedWindow(text, cv2.WINDOW_AUTOSIZE)
                cv2.imshow(text, img)
                SetWindowPos(FindWindow(None, text), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                cv2.waitKey(1)
            if not data[show]:
                cv2.destroyAllWindows()

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
