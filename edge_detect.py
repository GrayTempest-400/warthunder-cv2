from detect import *
import time
import cv2
import ctypes
import keyboard
from win32gui import FindWindow, SetWindowPos
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE

from key_input.press_key import InputKey
from key_input import Mouse, Keyboard


input_key = InputKey(0)


ads = 'ads'
show = 'show'
size = 'size'
init = {
    show: True,  # 显示, Down
    size: 200,  # 截图的尺寸, 屏幕中心截图周围大小
    ads:0.5,# 移动倍数, 调整方式: 瞄准目标旁边并按住 Shift 键, 当准星移动到目标点的过程, 稳定精准快速不振荡时, 就找到了合适的 ADS 值
}

c = cx_cy()


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

    center_x = 960 #要自行调整，数越大越靠右，越小越靠左    游戏特性无法更改  因为战雷鼠标不在屏幕中心点
    center_y = 300#要自行调整，数越大越靠上，越小越靠下

    print(center_x,center_y)


    # 计算屏幕中心到目标点的相对位移
    x_offset = x - center_x
    y_offset = y - center_y
    print(int(x_offset), int(y_offset))
    input_key.mouse_move(x_offset, y_offset)


def move1(x: int, y: int):
    if (x == 0) & (y == 0):
        return
    screen_width, screen_height = pyautogui.size()
    center_x = 960
    center_y = 540


    # 计算屏幕中心到目标点的相对位移
    x_offset = x - center_x
    y_offset = y - center_y
    print(x_offset, y_offset)
    driver.moveR(int(x_offset), int(y_offset),True)

def loop():

    while True:
        if keyboard.is_pressed('h'):
            print("按下了'h'键，退出函数执行")
            break

        capture_screen_around_centers(450)
        # 替换为您的图像文件路径
        image_path = 'detect_full.png'
        image = cv2.imread(image_path)
        result_image, x, y = find_purple_points(image_path, target_point=(450, 450))
        if result_image is not None:
            px, py = get_coordinate(450, x, y)
            move(px, py)

            input_key.click_key(Keyboard.X, 0.1)
            time.sleep(0.5)
            input_key.click_key(Keyboard.LSHIFT, 0.1)
            # 显示标记了最近紫色点的中心坐标的图像
            time.sleep(0.5)
            capture_screen_around_center(init[size])
            target, image1 = find_specific_purple_edges('detect.png', show=init[show]) #调用边缘检测求中心点
            if target is not None:
                x1, y1 = target
                aim = get_coordinate(init[size], x1, y1)#转为屏幕坐标
                px2 = aim[0]
                py2 = aim[1]
                time.sleep(0.5)
                print(px2, py2)

                move1(px2, py2)
                print("完成循环")
                input_key.mouse_key_click(Mouse.MOUSE_LEFT)
                time.sleep(1)
                cv2.namedWindow('detect', cv2.WINDOW_AUTOSIZE)
                im = cv2.resize(image1, (400, 400))
                cv2.imshow('detect', im)
                SetWindowPos(FindWindow(None, 'detect'), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                cv2.waitKey(1)
            else:
                resized_img = cv2.resize(result_image, (400, 400))
                cv2.imshow('detect', resized_img)
                SetWindowPos(FindWindow(None, 'detect'), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                cv2.waitKey(1)
        else:
            print("未能找到目标")
            img = cv2.resize(image, (400, 400))
            cv2.imshow('detect', img)
            SetWindowPos(FindWindow(None, 'detect'), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
            cv2.waitKey(1)
if __name__ == "__main__":
    loop()