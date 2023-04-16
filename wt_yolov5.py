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
    title: 'Apex Legends',  # 可在后台运行 print(GetWindowText(GetForegroundWindow())) 来检测前台游戏窗体标题
    weights: 'weights.apex.private.crony.1435244588.1127E7B7107206013DE38A10EDDEEEB3-v5-n-416-50000-3-0.1.2.engine',
    classes: 0,  # 要检测的标签的序号(标签序号从0开始), 多个时如右 [0, 1]
    confidence: 0.5,  # 置信度, 低于该值的认为是干扰
    size: 320,  # 截图的尺寸, 屏幕中心 size*size 大小
    radius: 160,  # 瞄准生效半径, 目标瞄点出现在以准星为圆心该值为半径的圆的范围内时才会锁定目标
    ads: 1.2,  # 移动倍数, 调整方式: 瞄准目标旁边并按住 Shift 键, 当准星移动到目标点的过程, 稳定精准快速不振荡时, 就找到了合适的 ADS 值
    center: None,  # 屏幕中心点
    region: None,  # 截图范围
    stop: False,  # 退出, End
    lock: False,  # 锁定, Shift, 按左键时不锁(否则扔雷时也会锁)
    show: False,  # 显示, Down
    head: False,  # 瞄头, Up
    pidc: False,  # 是否启用 PID Controller, 还未完善, Right
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

    def release(key):                                    #使用了Listener类来监听键盘事件，当按下键盘上的某个键时，会执行release函数。
                                                        # 如果按下的是end键，则会结束程序；如果按下的是shift键，则会将lock变量设为False；
                                                        # 如果按下的是up键，则会将head变量取反；# 如果按下的是down键，则会将show变量取反；
                                                        # 如果按下的是right键，则会将pidc变量取反；如果按下的是left键，则会将left变量取反；
                                                        # 如果按下的是page_down键，则会将debug变量取反。最后，使用Listener类的join方法来等待所有线程结束。
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
                                                             #定义了一个名为loop的函数，它有一个参数data。函数内部有三个变量：
                                                             # capturer、detector和winsound。capturer和detector是类的实例，
                                                             # 而winsound是Python内置模块的一部分。这个函数还包含一个调用winsound.Beep()
                                                             # 函数的语句，该语句将发出一声短暂的声音。
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

    def move(x: int, y: int):         #移动鼠标
        if (x == 0) & (y == 0):
            return
        driver.moveR(x, y, True)

    def inner(point):                           #This code is a Python function that takes a point as input and returns a boolean value indicating
                                                #此代码是一个Python函数，它以一个点作为输入，并返回一个布尔值，指示
                                                #该点是否在另一个点的某一范围内。具体来说，它检查距离在两点小于某一半径值
                                                 #代码使用，计算两点间距离的毕达哥拉斯定理
                                                # #维空间1.函数以一个点作为参数，然后计算距离。#在这个点和另一个点(圆心)之间使用这个公式：
                                                #距离=sqrt((x2-x1)^2+(y2-y1)^2)#如果。计算出的距离小于。圆的半径。然后函数返回True。指示
                                                #这点在范围内


        """
        判断该点是否在准星的瞄准范围内
        """
        a, b = data[center]
        x, y = point
        return (x - a) ** 2 + (y - b) ** 2 < data[radius] ** 2

    def follow(aims):            #此代码是一个 Python 函数，它将目标列表作为输入，并返回距离 circle1 中心最近的目标。该函数首先过滤掉置信水平低于特定阈值1的目标。然后，它通过计算每个目标的瞄准点来调整其
#根据它们在图像中的高度和位置的近似位置1。最后，它使用勾股定理1计算每个目标的目标点与圆心之间的距离。然后返回距离最小的目标1。


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
        cx, cy = data[center]                               #该函数返回一个元组，其中包含最接近所有目标中心点的目标对象及其关联的元数据1。
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
            img = capturer

            # img = Capturer.backup(data[region])  # 如果句柄截图是黑色, 不能正常使用, 可以使用本行的截图方法

            t2 = time.perf_counter_ns()
            aims, img = detector.detect(image=img, show=data[show])  # 目标检测, 得到截图坐标系内识别到的目标和标注好的图片(无需展示图片时img为none)
            t3 = time.perf_counter_ns()
            aims = detector.convert(aims=aims, region=data[region])  # 将截图坐标系转换为屏幕坐标系
            # print(f'{Timer.cost(t3 - t1)}, {Timer.cost(t2 - t1)}, {Timer.cost(t3 - t2)}')
            # 找到目标
            target = follow(aims)
           #敌我识别
            y = [i[1] for i in target] + 50
            x = [i[0] for i in target]




            def cv_show(name, image):
                cv2.imshow(name, image)
                cv2.waitKey(0)
                cv2.destoryAllWindows()

            image = cv2.imread('img')
            # 定义矩形坐标
            x, y, w, h = y, x, 100, 100

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
            if (cv2.countNonZero(mask_blue) > 0) or (cv2.countNonZero(mask_pink) > 0)and data[lock] and target :
                index, clazz, conf, sc, gc, sr, gr = target
                if inner(sc):
                    cx, cy = data[center]
                    sx, sy = sc                             #移动十字准线以跟随目标对象
                    x = sx - cx
                    y = sy - cy
                    if data[pidc]:
                        px = -int(pidx(x))
                        move(px, y)
                    else:
                        ax = int(x * data[ads])
                        ay = int(y * data[ads])
                        move(ax, ay)

            # 显示检测
            if data[show] and img is not None and (cv2.countNonZero(mask_blue) > 0) or (cv2.countNonZero(mask_pink) > 0):
                # 记录耗时
                cv2.putText(img, f'{Timer.cost(t3 - t1)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(img, f'{Timer.cost(t2 - t1)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                cv2.putText(img, f'{Timer.cost(t3 - t2)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
                # 瞄点划线
                if target:                                                #如果检测到目标对象，它会在图像上绘制十字准线和线条
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
    multiprocessing.freeze_support()                                    #用于创建三个进程并启动它们。第一个进程侦听鼠标事件，第二个进程侦听键盘事件，第三个进程运行更新进程之间共享数据的循环函数。
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
