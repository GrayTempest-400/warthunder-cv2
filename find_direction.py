import cv2 as cv
import numpy as np
from PIL import ImageGrab
import time
import find
import math

def findme(img):
    md = find('0.jpg')
    bbox = (md[0]+30, md[0]+30, md[0]+30, md[0]+30)
    img = ImageGrab.grab(bbox)





def ImageRotate(img, angle):   # img:输入图片；newIm：输出图片；angle：旋转角度(°)
    height, width = img.shape[:2]  # 输入(H,W,C)，取 H，W 的值
    center = (width // 2, height // 2)  # 绕图片中心进行旋转
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    image_rotation = cv.warpAffine(img, M, (width, height))
    return image_rotation


# 取圆形ROI区域函数：具体实现功能为输入原图，取原图最大可能的原型区域输出
def circle_tr(src):
    dst = np.zeros(src.shape, np.uint8)  # 感兴趣区域ROI
    mask = np.zeros(src.shape, dtype='uint8')  # 感兴趣区域ROI
    (h, w) = mask.shape[:2]
    (cX, cY) = (w // 2, h // 2)  # 是向下取整
    radius = int(min(h, w) / 2)
    cv.circle(mask, (cX, cY), radius, (255, 255, 255), -1)
    # 以下是copyTo的算法原理：
    # 先遍历每行每列（如果不是灰度图还需遍历通道，可以事先把mask图转为灰度图）
    for row in range(mask.shape[0]):
        for col in range(mask.shape[1]):
            # 如果掩图的像素不等于0，则dst(x,y) = scr(x,y)
            if mask[row, col] != 0:
                # dst_image和scr_Image一定要高宽通道数都相同，否则会报错
                dst[row, col] = src[row, col]
                # 如果掩图的像素等于0，则dst(x,y) = 0
            elif mask[row, col] == 0:
                dst[row, col] = 0
    return dst


# 金字塔下采样
def ImagePyrDown(image,NumLevels):
    for i in range(NumLevels):
        image = cv.pyrDown(image)       #pyrDown下采样
    return image


def RatationMatch(modelpicture, searchpicture):
# 旋转匹配函数（输入参数分别为模板图像、待匹配图像）
    searchtmp = []
    modeltmp = []

    searchtmp = ImagePyrDown(searchpicture, 3)
    modeltmp = ImagePyrDown(modelpicture, 3)

    newIm = circle_tr(modeltmp)
    # 使用matchTemplate对原始灰度图像和图像模板进行匹配
    res = cv.matchTemplate(searchtmp, newIm, cv.TM_SQDIFF_NORMED)
    min_val, max_val, min_indx, max_indx = cv.minMaxLoc(res)
    location = min_indx
    temp = min_val
    angle = 0  # 当前旋转角度记录为0

    tic = time.time()
    # 以步长为5进行第一次粗循环匹配
    for i in range(-180, 181, 5):
        newIm = ImageRotate(modeltmp, i)
        newIm = circle_tr(newIm)
        res = cv.matchTemplate(searchtmp, newIm, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_indx, max_indx = cv.minMaxLoc(res)
        if min_val < temp:
            location = min_indx
            temp = min_val
            angle = i
    toc = time.time()
    print('第一次粗循环匹配所花时间为：' + str(1000 * (toc - tic)) + 'ms')

    tic = time.time()
    # 在当前最优匹配角度周围10的区间以1为步长循环进行循环匹配计算
    for j in range(angle - 5, angle + 6):
        newIm = ImageRotate(modeltmp, j)
        newIm = circle_tr(newIm)
        res = cv.matchTemplate(searchtmp, newIm, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_indx, max_indx = cv.minMaxLoc(res)
        if min_val < temp:
            location = min_indx
            temp = min_val
            angle = j
    toc = time.time()
    print('在当前最优匹配角度周围10的区间以1为步长循环进行循环匹配所花时间为：' + str(1000 * (toc - tic)) + 'ms')

    tic = time.time()
    # 在当前最优匹配角度周围2的区间以0.1为步长进行循环匹配计算
    k_angle = angle - 0.9
    for k in range(0, 19):
        k_angle = k_angle + 0.1
        newIm = ImageRotate(modeltmp, k_angle)
        newIm = circle_tr(newIm)
        res = cv.matchTemplate(searchtmp, newIm, cv.TM_SQDIFF_NORMED)
        min_val, max_val, min_indx, max_indx = cv.minMaxLoc(res)
        if min_val < temp:
            location = min_indx
            temp = min_val
            angle = k_angle
    toc = time.time()
    print('在当前最优匹配角度周围2的区间以0.1为步长进行循环匹配所花时间为：' + str(1000 * (toc - tic)) + 'ms')

    # 用下采样前的图片来进行精匹配计算
    k_angle = angle - 0.1
    newIm = ImageRotate(modelpicture, k_angle)
    newIm = circle_tr(newIm)
    res = cv.matchTemplate(searchpicture, newIm, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_indx, max_indx = cv.minMaxLoc(res)
    location = max_indx
    temp = max_val
    angle = k_angle
    for k in range(1, 3):
        k_angle = k_angle + 0.1
        newIm = ImageRotate(modelpicture, k_angle)
        newIm = circle_tr(newIm)
        res = cv.matchTemplate(searchpicture, newIm, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_indx, max_indx = cv.minMaxLoc(res)
        if max_val > temp:
            location = max_indx
            temp = max_val
            angle = k_angle

    location_x = location[0] + 50
    location_y = location[1] + 50

    # 前面得到的旋转角度是匹配时模板图像旋转的角度，后面需要的角度值是待检测图像应该旋转的角度值，故需要做相反数变换
    angle = -angle

    match_point = {'angle': angle, 'point': (location_x, location_y)}
    return match_point


# 画图
def draw_result(src, temp, match_point):
    cv.rectangle(src, match_point,
                  (match_point[0] + temp.shape[1], match_point[1] + temp.shape[0]),
                  (0, 255, 0), 2)
    cv.imshow('result', src)
    cv.waitKey()



def get_realsense(src, temp):
    ModelImage = temp
    SearchImage = src#srcx
    ModelImage_edge = cv.GaussianBlur(ModelImage, (5, 5), 0)
    ModelImage_edge = cv.Canny(ModelImage_edge, 10, 200, apertureSize=3)
    SearchImage_edge = cv.GaussianBlur(SearchImage, (5, 5), 0)

    (h1, w1) = SearchImage_edge.shape[:2]
    SearchImage_edge = cv.Canny(SearchImage_edge, 10, 180, apertureSize=3)
    serch_ROIPart = SearchImage_edge[50:h1 - 50, 50:w1 - 50]  # 裁剪图像

    tic = time.time()
    match_points = RatationMatch(ModelImage_edge, serch_ROIPart)
    toc = time.time()
    print('匹配所花时间为：' + str(1000 * (toc - tic)) + 'ms')
    print('匹配的最优区域的起点坐标为：' + str(match_points['point']))
    print('相对旋转角度为：' + str(match_points['angle']))
    TmpImage_edge = ImageRotate(SearchImage_edge, match_points['angle'])
    cv.imshow("TmpImage_edge", TmpImage_edge)
    cv.waitKey()
    draw_result(SearchImage, ModelImage_edge, match_points['point'])
    return match_points

def findtheater(x1, y1, x2, y2):
    """ 已知两点坐标计算角度 -
    :param x1: 原点横坐标值
    :param y1: 原点纵坐标值
    :param x2: 目标点横坐标值
    :param y2: 目标纵坐标值
    """
    angle = 0.0
    dx = x2 - x1
    dy = y2 - y1
    if x2 == x1:
        angle = math.pi / 2.0
        if y2 == y1:
            angle = 0.0
        elif y2 < y1:
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dx / dy)
    elif x2 > x1 and y2 < y1:
        angle = math.pi / 2 + math.atan(-dy / dx)
    elif x2 < x1 and y2 < y1:
        angle = math.pi + math.atan(dx / dy)
    elif x2 < x1 and y2 > y1:
        angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)
    return angle * 180 / math.pi