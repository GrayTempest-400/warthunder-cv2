import cv2
import mss
import numpy as np
import win32con
import win32gui
import win32print


def identify_gap(bg, tp):
    '''
    bg: 背景图片
    tp: 缺口图片
    out:输出图片
    '''
    # 读取背景图片和缺口图片
    # bg_img = cv2.imread(bg)  # 背景图片
    tp_img = cv2.imread(tp)  # 缺口图片



    # 识别图片边缘
    bg_edge = cv2.Canny(bg, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    if max_val < 0.6:
        return -0
    # 绘制方框
    th, tw = tp_pic.shape[:2]
    tl = max_loc  # 左上角点的坐标
    br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
    cv2.rectangle(bg, tl, br, (0, 0, 255), 2)  # 绘制矩形

    # cv2.imwrite(out, bg_img)  # 保存在本地
    # 返回缺口的X坐标
    return tl,br


# 自定义匹配程度m
def matching(bg, tp, m):
    '''
    bg: 背景图片
    tp: 缺口图片
    out:输出图片
    '''
    # 读取背景图片和缺口图片
    # bg_img = cv2.imread(bg)  # 背景图片
    tp_img = cv2.imread(tp)  # 缺口图片

    # 识别图片边缘
    bg_edge = cv2.Canny(bg, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_BGR2BGRA)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_BGR2BGRA)

    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    if max_val < m:
        return -0
    # 绘制方框
    th, tw = tp_pic.shape[:2]
    tl = max_loc  # 左上角点的坐标
    br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
    cv2.rectangle(bg, tl, br, (0, 0, 255), 2)  # 绘制矩形

    # cv2.imwrite(out, bg_img)  # 保存在本地
    # 返回缺口的X坐标
    return tl, br


# 定位搜寻图片位置的中心点
def find(p):
    sec = mss.mss()
    screen = {
        'left': 0,
        'top': 0,
        'width': 1027,
        'height': 794
    }
    img = sec.grab(screen)
    img = np.array(img)
    a = identify_gap(img, p)
    if a == -0:
        findx = False
    else:
        x = a[0][0] + ((a[1][0] - a[0][0]) / 2)
        y = a[0][1] + ((a[1][1] - a[0][1]) / 2)
        pos = ((int(x), int(y)))
        return pos


# 在限定区域内寻找对应图片
def find_limit(p, l, t, w, h):
    sec = mss.mss()
    screen = {
        'left': l,
        'top': t,
        'width': w,
        'height': h
    }
    img = sec.grab(screen)
    img = np.array(img)
    a = identify_gap(img, p)
    if a == -0:
        # print('未找到位置')
        return None
    else:
        # hwnd = win32gui.FindWindow("DagorWClass", None)
        x = a[0][0] + ((a[1][0] - a[0][0]) / 2)
        y = a[0][1] + ((a[1][1] - a[0][1]) / 2)
        pos = ((int(x), int(y)))
        return pos


# 全屏范围寻找，自定义匹配程度
def find_match(p, m):
    sec = mss.mss()
    screen = {
        'left': 0,
        'top': 0,
        'width': 1027,
        'height': 794
    }
    img = sec.grab(screen)
    img = np.array(img)
    # cv2.imshow('111',img)
    # cv2.waitKey(3000)
    a = matching(img, p, m)
    if a == -0:
        findx = False
    else:
        # hwnd = win32gui.FindWindow("DagorWClass", None)
        x = a[0][0] + ((a[1][0] - a[0][0]) / 2)
        y = a[0][1] + ((a[1][1] - a[0][1]) / 2)
        pos = ((int(x), int(y)))
        return pos


# 限定范围寻找，自定义匹配程度
def find_lit_mat(p, m, l, t, w, h):
    sec = mss.mss()
    screen = {
        'left': l,
        'top': t,
        'width': w,
        'height': h
    }
    img = sec.grab(screen)
    img = np.array(img)
    # cv2.imshow('111',img)
    # cv2.waitKey(3000)
    a = matching(img, p, m)
    if a == -0:
        findx = False
    else:
        # hwnd = win32gui.FindWindow("DagorWClass", None)
        x = a[0][0] + ((a[1][0] - a[0][0]) / 2)
        y = a[0][1] + ((a[1][1] - a[0][1]) / 2)
        pos = ((int(x), int(y)))
        return pos

def check(p,m):
    a = find_match(p,m)
    if a is not None:
        return True
    elif a is None:
        return False
    else:
        return False


def check_limit(p,m,l,t,w,h):
    a = find_lit_mat(p,m,l,t,w,h)
    if a is not None:
        return True
    elif a is None:
        return False
    else:
        return False


def locate(p,m):
    sec = mss.mss()
    zone = {
            'left':0,#2112
            'top':0,#995
            'width':1027,#2550
            'height':792#1435
        }

    bg = sec.grab(zone)
    bg1 = np.array(bg)

    img = cv2.imread(p, cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 根据像素的范围进行过滤，把符合像素范围的保留，不符合的赋值0或者255
    # 根据hsv颜色表找出最大值和最小值
    mask = cv2.inRange(hsv, (35, 43, 46), (77, 255, 255))
    mask = cv2.bitwise_not(mask)
    result = cv2.bitwise_and(img, img, mask=mask)
    # cv2.imshow('1',result)
    # cv2.waitKey(2000)
    # cv2.destroyAllWindows()
    # 读取背景图片和缺口图片
    # bg = cv2.imread('map.png')  # 背景图片
    # tp_img = cv2.imread(tp)  # 缺口图片

    # 识别图片边缘
    # bg_edge = cv2.Canny(bg, 100, 200)
    # tp_edge = cv2.Canny(result, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg1, cv2.COLOR_BGR2BGRA)
    tp_pic = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    # cv2.imshow('1',bg_pic)
    # cv2.waitKey(5000)
    # cv2.destroyAllWindows()
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    if max_val < m:
        # print((-0,-0))
        return None
    else:
        th, tw = result.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        b = cv2.rectangle(bg1, tl, br, (0, 0, 255), 2)
        x,y = (tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2
        a = (int(x), int(y))
        return a


def locatesrc(p,m,hwnd):
    hDC = win32gui.GetDC(0)
    wide = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    high = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    apprect = win32gui.GetWindowRect(hwnd)
    l = apprect[0]  ############相对位置截图
    t = apprect[1]
    w = apprect[2]
    h = apprect[3]
    print(l, t, w, h)
    sec = mss.mss()
    zone = {
        'left': l,
        'top': t,
        'width': w,
        'height': h
    }

    bg = sec.grab(zone)
    bg1 = np.array(bg)

    img = cv2.imread(p, cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 根据像素的范围进行过滤，把符合像素范围的保留，不符合的赋值0或者255
    # 根据hsv颜色表找出最大值和最小值
    mask = cv2.inRange(hsv, (35, 43, 46), (77, 255, 255))
    mask = cv2.bitwise_not(mask)
    result = cv2.bitwise_and(img, img, mask=mask)
    # cv2.imshow('1',result)
    # cv2.waitKey(2000)
    # cv2.destroyAllWindows()
    # 读取背景图片和缺口图片
    # bg = cv2.imread('map.png')  # 背景图片
    # tp_img = cv2.imread(tp)  # 缺口图片

    # 识别图片边缘
    # bg_edge = cv2.Canny(bg, 100, 200)
    # tp_edge = cv2.Canny(result, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg1, cv2.COLOR_BGR2BGRA)
    tp_pic = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    # cv2.imshow('1',bg_pic)
    # cv2.waitKey(5000)
    # cv2.destroyAllWindows()
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    if max_val < m:
        # print((-0,-0))
        return None
    else:
        th, tw = result.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        b = cv2.rectangle(bg1, tl, br, (0, 0, 255), 2)
        x,y = (tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2
        a = (int(x), int(y))
        return a


def locate_limit(p,m,x1,y1,x2,y2):
    sec = mss.mss()
    zone = {
            'left':x1,#2112
            'top':y1,#995
            'width':x2,#2550
            'height':y2#1435
        }

    bg = sec.grab(zone)
    bg1 = np.array(bg)
    # cv2.imshow('1', bg1)
    # cv2.waitKey(3000)
    # cv2.destroyAllWindows()

    img = cv2.imread(p, cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 根据像素的范围进行过滤，把符合像素范围的保留，不符合的赋值0或者255
    # 根据hsv颜色表找出最大值和最小值
    mask = cv2.inRange(hsv, (35, 43, 46), (77, 255, 255))
    mask = cv2.bitwise_not(mask)
    result = cv2.bitwise_and(img, img, mask=mask)
    # cv2.imshow('1',result)
    # cv2.waitKey(2000)
    # cv2.destroyAllWindows()
    # 读取背景图片和缺口图片
    # bg = cv2.imread('map.png')  # 背景图片
    # tp_img = cv2.imread(tp)  # 缺口图片

    # 识别图片边缘
    # bg_edge = cv2.Canny(bg, 100, 200)
    # tp_edge = cv2.Canny(result, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg1, cv2.COLOR_BGR2BGRA)
    tp_pic = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    # cv2.imshow('1',bg_pic)
    # cv2.waitKey(5000)
    # cv2.destroyAllWindows()
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    if max_val < m:
        # print((-0,-0))
        return None
    else:
        th, tw = result.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
        b = cv2.rectangle(bg1, tl, br, (0, 0, 255), 2)
        x,y = (tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2
        a = (int(x), int(y))
        return a