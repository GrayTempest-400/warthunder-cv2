import cv2
import numpy as np
from collections import Counter
import win32con
import win32gui
import mss
import pyautogui

def detect_buttons(screenshot_path, template_path, threshold=0.8):
    # 读取游戏界面的屏幕截图和按钮的模板图像
    screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    # 获取模板图像的宽度和高度
    template_width, template_height = template.shape[::-1]

    # 使用模板匹配方法进行匹配
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

    # 使用Numpy的where函数找到匹配结果大于阈值的位置
    locations = np.where(res >= threshold)

    # 创建一个列表，保存所有检测到的按钮位置信息
    button_positions = []

    # 遍历所有匹配位置，并将按钮位置信息添加到列表中
    for (x, y) in zip(*locations[::-1]):
        button_positions.append((x, y, x + template_width, y + template_height))

    # 计算中心点并将中心点坐标替换按钮位置信息中的右下角坐标
    button_centers = []
    for (x1, y1, x2, y2) in button_positions:
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        button_centers.append((center_x, center_y))
    if len(button_centers) > 4:
        return False

    return button_centers




def find_template_in_image(image_path, template_path):
    img = cv2.imread(image_path, 0)
    img2 = img.copy()
    template = cv2.imread(template_path, 0)
    w, h = template.shape[::-1]

    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
               'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    matches = []

    for meth in methods:
        img = img2.copy()
        method = eval(meth)
        # 模板匹配
        res = cv2.matchTemplate(img, template, method)
        # 寻找最值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # 使用不同的比较方法，对结果的解释不同
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        center_point = ((top_left[0] + bottom_right[0]) // 2, (top_left[1] + bottom_right[1]) // 2)
        matches.append(center_point)

    return matches

def most_common_array(arr_list):
    # 使用Counter计算数组出现次数
    array_counter = Counter(arr_list)
    # 获取出现次数最多的数组和对应的次数
    most_common_array, count = array_counter.most_common(1)[0]
    return most_common_array

def active():  # 窗口置顶
    hwnd = win32gui.FindWindow(None,'War Thunder')
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    win32gui.SetForegroundWindow(hwnd)

def find(p):
    sec = mss.mss()
    screen = {
        'left': 0,
        'top': 0,
        'width': 1285,
        'height': 794
    }
    img = sec.grab(screen)
    # Save the grabbed image to a file
    img_path = 'screenshot.png'
    cv2.imwrite(img_path, np.array(img))

    a = find_template_in_image(img_path, p)

    return a
def find1 (p,threshold):
    sec = mss.mss()
    screen = {
        'left': 0,
        'top': 0,
        'width': 1285,
        'height': 794
    }
    img = sec.grab(screen)
    # Save the grabbed image to a file
    img_path = 'screenshot.png'
    cv2.imwrite(img_path, np.array(img))

    a = detect_buttons(img_path, p,threshold)

    return a

def check(p):
    b = (find(p))
    a = most_common_array(b)
    if a is not None:
        print(a[0], a[1])
        pyautogui.moveTo(a[0], a[1])
        pyautogui.click()
        return True
    elif a is None:
        return False
    else:
        return False


# 示例使用




# 示例使用
main_image_path = 'pic/t114.png'
template_image_path = 'pic/join.png'
print(detect_buttons(main_image_path,template_image_path,threshold=0.8))
# 给定的列表
arr_list = (find_template_in_image(main_image_path, template_image_path))

# 获取出现次数最多的数组
result = most_common_array(arr_list)
print(result)