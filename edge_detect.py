from detect import *
import time
import cv2
import ctypes
import keyboard
from win32gui import FindWindow, SetWindowPos
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE




show = 'show'
size = 'size'
init = {
    show: True,  # 显示, Down
    size: 200,  # 截图的尺寸, 屏幕中心截图周围大小
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
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2

    # 计算屏幕中心到目标点的相对位移
    x_offset = x - center_x
    y_offset = y - center_y
    driver.moveR(int(x_offset), int(y_offset), True)




def loop():
    while True:
        if keyboard.is_pressed('h'):
            print("按下了'h'键，退出函数执行")
            break

        capture_screen_around_centers(540)
        # 替换为您的图像文件路径
        image_path = 'detect_full.png'
        image = cv2.imread(image_path)
        result_image, x, y = find_purple_points(image_path, target_point=(540, 540))
        if result_image is not None:
            print(x, y)
            px, py = get_coordinate(540, x, y)
            print(px, py)

            # 显示标记了最近紫色点的中心坐标的图像
            time.sleep(0.5)
            capture_screen_around_center(init[size])
            target, image1 = find_specific_purple_edges('detect.png', show=init[show]) #调用边缘检测求中心点
            if target is not None:
                x, y = target
                aim = get_coordinate(init[size], x, y)
                x = aim[0]
                y = aim[1]
                time.sleep(0.5)
                print(x, y)
                cv2.line(image1, aim, (c[0], c[1]), (255, 255, 0), 2)   #画图
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