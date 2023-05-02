import ctypes
import math
import multiprocessing
import time
from multiprocessing import Process
import cv2
import pynput
from win32gui import GetCursorPos, FindWindow, SetWindowPos, GetWindowText, GetForegroundWindow
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE
import winsound
from simple_pid import PID  # pip install simple-pid

fov = 'fov'
end = 'end'
box = 'box'
aim = 'aim'
show = 'show'
view = 'view'
fire = 'fire'
head = 'head'
size = 'size'
heads = {'head', '1'}
bodies = {'body', '0'}
region = 'region'
center = 'center'
radius = 'radius'
weights = 'weights'
predict = 'predict'
vertical = 'vertical'
timestamp = 'timestamp'
horizontal = 'horizontal'
confidence = 'confidence'
sensitivity = 'sensitivity'
init = {
    fov: 110,  # 游戏内的 FOV
    horizontal: 16420,  # 游戏内以鼠标灵敏度为1测得的水平旋转360°对应的鼠标移动距离, 多次测量验证. 经过测试该值与FOV无关. 移动像素理论上等于该值除以鼠标灵敏度Horizontal Vertical
    vertical: 7710 * 2,  # 垂直, 注意垂直只能测一半, 即180°范围, 所以结果需要翻倍
    sensitivity: 2,  # 当前游戏鼠标灵敏度
    radius: 400,  # 瞄准生效半径, 目标瞄点出现在以准星为圆心该值为半径的圆的范围内时才会自动瞄准
    weights: 'model.for.apex.dummy.engine',  # 权重文件
    confidence: 0.5,  # 置信度, 低于该值的认为是干扰
    size: 400,  # 截图的尺寸, 屏幕中心 size*size 大小
    center: None,  # 屏幕中心点
    region: None,  # 截图范围
    end: False,  # 退出标记, End
    box: False,  # 显示开关, Up
    show: False,  # 显示状态
    aim: False,  # 瞄准开关, Down, X2(侧上键)
    fire: False,  # 开火状态
    timestamp: None,  # 开火时间
    view: False,  # 预瞄状态, F, 手枪狙击枪可提前预瞄一下
    head: False,  # 是否瞄头, Right
    predict: False,  # 是否预瞄, Left
}


def game():
    return 'Apex Legends' in GetWindowText(GetForegroundWindow())


def mouse(data):

    def down(x, y, button, pressed):
        if not game():
            return
        if button == pynput.mouse.Button.left:
            data[fire] = pressed
            if pressed:
                data[timestamp] = time.time_ns()
        elif button == pynput.mouse.Button.x2:
            if pressed:
                data[aim] = not data[aim]
                winsound.Beep(800 if data[aim] else 400, 200)

    with pynput.mouse.Listener(on_click=down) as m:
        m.join()


def keyboard(data):

    def press(key):
        if not game():
            return
        if key == pynput.keyboard.KeyCode.from_char('f'):
            data[view] = True

    def release(key):
        if key == pynput.keyboard.Key.end:
            # 结束程序
            data[end] = True
            winsound.Beep(400, 200)
            return False
        if not game():
            return
        if key == pynput.keyboard.KeyCode.from_char('f'):
            data[view] = False
        elif key == pynput.keyboard.Key.up:
            data[box] = not data[box]
            winsound.Beep(800 if data[box] else 400, 200)
        elif key == pynput.keyboard.Key.down:
            data[aim] = not data[aim]
            winsound.Beep(800 if data[aim] else 400, 200)
        elif key == pynput.keyboard.Key.left:
            data[predict] = not data[predict]
            winsound.Beep(800 if data[predict] else 600, 200)
        elif key == pynput.keyboard.Key.right:
            data[head] = not data[head]
            winsound.Beep(800 if data[head] else 600, 200)

    with pynput.keyboard.Listener(on_release=release, on_press=press) as k:
        k.join()


def producer(data, queue):
    from toolkit import Detector, Timer
    detector = Detector(data[weights])
    winsound.Beep(800, 200)
    while True:
        if data[end]:
            break
        if data[box] or data[aim]:
            begin = time.perf_counter_ns()
            aims, img = detector.detect(region=data[region], classes=heads.union(bodies), show=data[box], label=False)
            if data[box]:
                cv2.putText(img, f'{Timer.cost(time.perf_counter_ns() - begin)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)
            try:
                queue.put((aims, img), block=True, timeout=1)
            except Exception as e:
                print(f'Producer Exception, {e.args}')


def consumer(data, queue):

    from toolkit import Monitor, Predictor, Timer
    data[center] = Monitor.center()
    c1, c2 = data[center]
    data[region] = c1 - data[size] // 2, c2 - data[size] // 2, data[size], data[size]
    predictor = Predictor()

    try:
        driver = ctypes.CDLL('logitech.driver.dll')
        ok = driver.device_open() == 1
        if not ok:
            print('初始化失败, 未安装罗技驱动')
    except FileNotFoundError:
        print('初始化失败, 缺少文件')

    def move(x, y, absolute=False):
        if (x == 0) & (y == 0):
            return
        mx, my = x, y
        if absolute:
            ox, oy = GetCursorPos()
            mx = x - ox
            my = y - oy
        driver.moveR(mx, my, True)

    def oc():
        ac, _ = data[center]
        return ac / math.tan((data[fov] / 2 * math.pi / 180))

    def rx(x):
        angle = math.atan(x / oc()) * 180 / math.pi
        return int(angle * data[horizontal] / data[sensitivity] / 360)

    def ry(y):
        angle = math.atan(y / oc()) * 180 / math.pi
        return int(angle * data[vertical] / data[sensitivity] / 360)

    def inner(point):
        """
        判断该点是否在准星的瞄准范围内
        """
        a, b = data[center]
        x, y = point
        return (x - a) ** 2 + (y - b) ** 2 < data[radius] ** 2

    def follow(targets, last):
        """
        从 targets 里选距离 last 最近的
        """
        if len(targets) == 0:
            return None
        if last is None:
            lx, ly = data[center]
        else:
            _, lsc, _, _ = last
            lx, ly = lsc
        index = 0
        minimum = 0
        for i, item in enumerate(targets):
            _, sc, _, _ = item
            sx, sy = sc
            distance = (sx - lx) ** 2 + (sy - ly) ** 2
            if minimum == 0:
                index = i
                minimum = distance
            else:
                if distance < minimum:
                    index = i
                    minimum = distance
        return targets[index]

    pidx = PID(1, 0, 0, setpoint=0, sample_time=0.001)
    pidx.output_limits = (-100, 100)

    title = 'Realtime ScreenGrab Detect'

    last = None
    while True:
        if data[end]:
            cv2.destroyAllWindows()
            break
        if not (data[box] or data[aim]):
            continue
        product = None
        try:
            product = queue.get(block=True, timeout=1)
        except Exception as e:
            print(f'Consumer Exception, {e.args}')
        if not product:
            continue
        aims, img = product
        targets = []
        for clazz, conf, sc, gc, sr, gr in aims:
            # 置信度过滤
            if conf < data[confidence]:
                continue
            # 拿到指定的分类
            _, _, _, height = sr
            if data[head]:
                # 两种方式, 1:拿到Head框, 2:从Body框里推测Head的位置
                # if clazz in heads:
                #     targets.append((height, sc, gc, gr))
                if clazz in bodies:
                    cx, cy = sc
                    targets.append((height, (cx, cy - (height // 2 - height // 8)), gc, gr))
            else:
                if clazz in bodies:
                    cx, cy = sc
                    targets.append((height, (cx, cy - (height // 2 - height // 3)), gc, gr))  # 检测身体的时候, 因为中心位置不太好, 所以对应往上调一点
        target = None
        predicted = None
        if len(targets) != 0:
            # 拿到瞄准目标
            # 尽量跟一个目标, 不要来回跳, 目标消失后在原地停顿几个循环, 如目标仍未再次出现, 才认为目标消失, 开始找下一个目标
            target = follow(targets, last)
            # 重置上次瞄准的目标
            last = target
            # 解析目标里的信息
            if target:
                _, sc, _, gr = target
                predicted = predictor.predict(sc)  # 目标预测点
                # 计算移动距离, 展示预瞄位置
                if data[box]:
                    sx, sy = sc  # 目标所在点
                    px, py = predicted  # 目标将在点
                    dx = (px - sx) * 2
                    dy = (py - sy) * 2
                    gl, gt, gw, gh = gr
                    px1 = gl + dx
                    py1 = gt + dy
                    px2 = px1 + gw
                    py2 = py1 + gh
                    cv2.rectangle(img, (px1, py1), (px2, py2), (0, 256, 0), 2)
        # 检测瞄准开关
        if data[aim] and (data[view] or data[fire]):
            if target:
                _, sc, _, _ = target
                if inner(sc):
                    # 计算要移动的像素
                    cx, cy = data[center]  # 准星所在点(屏幕中心)
                    sx, sy = sc  # 目标所在点
                    px, py = predicted  # 目标将在点
                    if data[predict]:
                        x = int(px - cx)
                        y = int(py - cy)
                    else:
                        x = sx - cx
                        y = sy - cy
                    ox = rx(x)
                    oy = ry(y)
                    px = int(pidx(ox))
                    px = int(ox)
                    py = int(oy)
                    print(f'目标:{sc}, 预测:{predicted}, 移动像素:{(x, y)}, FOV:{(ox, oy)}, PID:{(px, py)}')
                    move(px, py)
        # 检测显示开关
        if data[box]:
            if img is None:
                continue
            data[show] = True
            cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
            cv2.imshow(title, img)
            SetWindowPos(FindWindow(None, title), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
            cv2.waitKey(1)
        if not data[box] and data[show]:
            data[show] = False
            cv2.destroyAllWindows()


if __name__ == '__main__':
    multiprocessing.freeze_support()  # windows 平台使用 multiprocessing 必须在 main 中第一行写这个
    manager = multiprocessing.Manager()
    queue = manager.Queue(maxsize=1)
    data = manager.dict()  # 创建进程安全的共享变量
    data.update(init)  # 将初始数据导入到共享变量
    # 将键鼠监听和压枪放到单独进程中跑
    pm = Process(target=mouse, args=(data,), name='Mouse')
    pk = Process(target=keyboard, args=(data,), name='Keyboard')
    pp = Process(target=producer, args=(data, queue,), name='Producer')
    pc = Process(target=consumer, args=(data, queue,), name='Consumer')
    pm.start()
    pk.start()
    pp.start()
    pc.start()
    pk.join()  # 不写 join 的话, 使用 dict 的地方就会报错 conn = self._tls.connection, AttributeError: 'ForkAwareLocal' object has no attribute 'connection'
    pm.terminate()  # 鼠标进程无法主动监听到终止信号, 所以需强制结束
