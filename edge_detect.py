from detect import *
import time
import cv2
import keyboard
from win32gui import FindWindow, SetWindowPos
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE

from key_input.press_key import InputKey
from key_input import Mouse, Keyboard


input_key = InputKey(0)



show = 'show'
size = 'size'
size_point = 'size_point'
init = {
    show: True,  # 显示, Down
    size: 200,  # 截图的尺寸, 屏幕中心截图周围大小
    size_point: 450,

}

c = cx_cy()

def move(x: int, y: int):      #不开镜模式下鼠标移动
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


def move1(x: int, y: int):    #开镜模式下鼠标移动
    if (x == 0) & (y == 0):
        return
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2

    # 计算屏幕中心到目标点的相对位移
    x_offset = x - center_x
    y_offset = y - center_y
    print(x_offset, y_offset)
    input_key.mouse_move(x_offset, y_offset)

def loop():      #主函数

    while True:
        if keyboard.is_pressed('h'):
            print("按下了'h'键，退出函数执行")
            break

        capture_screen_around_centers(init[size_point]) #截图
        # 替换为您的图像文件路径
        image_path = 'detect_full.png'         #原理是截图然后处理最后显示
        image = cv2.imread(image_path)
        result_image, x, y = find_purple_points(image_path, target_point=(init[size_point], init[size_point]))#找离屏幕中心最近的紫色点
        if result_image is not None:
            px, py = get_coordinate(init[size_point], x, y)   #转为屏幕坐标
            move(px, py)                                      #移动
            input_key.click_key(Keyboard.X, 0.1)              #按X
            time.sleep(0.5)
            input_key.click_key(Keyboard.LSHIFT, 0.1)         #开镜
            # 显示标记了最近紫色点的中心坐标的图像
            time.sleep(0.5)
            #开镜后处理
            capture_screen_around_center(init[size])#截图
            target, image1 = find_specific_purple_edges('detect.png', show=init[show]) #调用边缘检测求中心点
            if target is not None:
                x1, y1 = target
                aim = get_coordinate(init[size], x1, y1)#转为屏幕坐标
                px2 = aim[0]
                py2 = aim[1]
                time.sleep(0.5)
                print(px2, py2)
                move1(px2, py2)                          #移动
                print("完成循环")
                input_key.mouse_key_click(Mouse.MOUSE_LEFT)      #开火
                time.sleep(1)
                input_key.click_key(Keyboard.LSHIFT, 0.1)        #关镜
                #显示

                if init[show] == True :
                   cv2.namedWindow('detect', cv2.WINDOW_AUTOSIZE)
                   im = cv2.resize(image1, (400, 400))
                   cv2.imshow('detect', im)
                   SetWindowPos(FindWindow(None, 'detect'), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                   cv2.waitKey(1)
            else:
                # 显示
                if init[show] == True:
                   resized_img = cv2.resize(result_image, (400, 400))
                   cv2.imshow('detect', resized_img)
                   SetWindowPos(FindWindow(None, 'detect'), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                   cv2.waitKey(1)
        else:
                #显示
            print("未能找到目标")
            if init[show] == True:
                img = cv2.resize(image, (400, 400))
                cv2.imshow('detect', img)
                SetWindowPos(FindWindow(None, 'detect'), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                cv2.waitKey(1)

while True:
    loop()