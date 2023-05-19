import math
from find import find_match,find_square
import mss
import mss.tools
import numpy as np
import cv2


def capture_coordinate(x, y, width, height):

    """
       使用mss库进行屏幕截图

       参数:
       x (int): 截图区域左上角 x 坐标
       y (int): 截图区域左上角 y 坐标
       width (int): 截图区域宽度
       height (int): 截图区域高度

       返回：储存名为me的图片
    """


    with mss.mss() as sct:
        monitor = {"left": x, "top": y, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        im = np.array(screenshot)
        im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
        cv2.imwrite("me.png", im)  # 保存为名为"me.png"的图片
        return im


# 图片旋转函数
def ImageRotate(img, angle):
    """
        对图像进行旋转

        参数:
        img (numpy.ndarray): 输入图像
        angle (float): 旋转角度（单位：度）

        返回:
        numpy.ndarray: 旋转后的图像
    """
    height, width = img.shape[:2]
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    image_rotation = cv2.warpAffine(img, M, (width, height))
    return image_rotation

# 取圆形ROI区域函数
def circle_tr(src):
    """
        获取圆形ROI区域

        参数:
        src (numpy.ndarray): 输入图像

        返回:
        numpy.ndarray: 圆形ROI区域图像
    """
    dst = np.zeros(src.shape, np.uint8)
    mask = np.zeros(src.shape, dtype='uint8')
    (h, w) = mask.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    radius = int(min(h, w) / 2)
    cv2.circle(mask, (cX, cY), radius, (255, 255, 255), -1)
    for row in range(mask.shape[0]):
        for col in range(mask.shape[1]):
            if mask[row, col] != 0:
                dst[row, col] = src[row, col]
            elif mask[row, col] == 0:
                dst[row, col] = 0
    return dst

# 旋转匹配函数
def RotationMatch(model_image, search_image):   #返回方向和点
    '''
    输入model_image 作为模板图像
    输入search_image 作为寻找的图像
    返回相对方向和起点坐标
    '''
    search_tmp = []
    model_tmp = []

    search_tmp = ImagePyrDown(search_image, 3)
    model_tmp = ImagePyrDown(model_image, 3)

    newIm = circle_tr(model_tmp)

    res = cv2.matchTemplate(search_tmp, newIm, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    location = min_loc
    temp = min_val
    angle = 0

    tic = cv2.getTickCount()

    for i in range(-180, 181, 5):
        newIm = ImageRotate(model_tmp, i)
        newIm = circle_tr(newIm)
        res = cv2.matchTemplate(search_tmp, newIm, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if min_val < temp:
            location = min_loc
            temp = min_val
            angle = i

    toc = cv2.getTickCount()

    print('第一次粗循环匹配所花时间为：', (toc - tic) / cv2.getTickFrequency() * 1000, 'ms')

    tic = cv2.getTickCount()

    for j in range(angle - 5, angle + 6):
        newIm = ImageRotate(model_tmp, j)
        newIm = circle_tr(newIm)
        res = cv2.matchTemplate(search_tmp, newIm, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if min_val < temp:
            location = min_loc
            temp = min_val
            angle = j

    toc = cv2.getTickCount()

    print('在当前最优匹配角度周围10的区间以1为步长循环进行循环匹配所花时间为：', (toc - tic) / cv2.getTickFrequency() * 1000, 'ms')

    tic = cv2.getTickCount()

    k_angle = angle - 0.9
    for k in range(0, 19):
        k_angle = k_angle + 0.1
        newIm = ImageRotate(model_tmp, k_angle)
        newIm = circle_tr(newIm)
        res = cv2.matchTemplate(search_tmp, newIm, cv2.TM_SQDIFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if min_val < temp:
            location = min_loc
            temp = min_val
            angle = k_angle

    toc = cv2.getTickCount()

    print('在当前最优匹配角度周围2的区间以0.1为步长进行循环匹配所花时间为：', (toc - tic) / cv2.getTickFrequency() * 1000, 'ms')

    k_angle = angle - 0.1
    newIm = ImageRotate(model_image, k_angle)
    newIm = circle_tr(newIm)
    res = cv2.matchTemplate(search_image, newIm, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    location = max_loc
    temp = max_val
    angle = k_angle

    for k in range(1, 3):
        k_angle = k_angle + 0.1
        newIm = ImageRotate(model_image, k_angle)
        newIm = circle_tr(newIm)
        res = cv2.matchTemplate(search_image, newIm, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > temp:
            location = max_loc
            temp = max_val
            angle = k_angle

    location_x = location[0] + 50
    location_y = location[1] + 50

    angle = -angle

    match_point = {'angle': angle, 'point': (location_x, location_y)}
    return match_point

# 画图
def draw_result(src, temp, match_point):
    '''
    传入图片，模板图，方向和起点坐标
    传出：cv2画图
    '''
    cv2.rectangle(src, match_point,
                  (match_point[0] + temp.shape[1], match_point[1] + temp.shape[0]),
                  (0, 255, 0), 2)
    cv2.imshow('result', src)
    cv2.waitKey()

# 金字塔下采样，建议别用，战雷的地图最多截图个50x50这玩意没必要
def ImagePyrDown(image, num_levels):
    '''
    传入图片，缩小等级
    返回缩小后图片
    '''
    for i in range(num_levels):
        image = cv2.pyrDown(image)
    return image

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    计算两个点之间的方位角
    参数:
        原点：
        lat1: 第一个点的x
        lon1: 第一个点的y
        要找的方位角点：
        lat2: 第二个点的x
        lon2: 第二个点的y
    返回值:
        int: 方位角（四舍五入到整数）
    """
    # 将x和y转换为弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 计算x差值
    d_lon = lon2_rad - lon1_rad

    # 计算方位角
    y = math.sin(d_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon)
    bearing_rad = math.atan2(y, x)

    # 将弧度转换为角度
    bearing_deg = math.degrees(bearing_rad)

    # 确保方位角在0到360度之间
    if bearing_deg < 0:
        bearing_deg += 360
        # 四舍五入到整数
    rounded_bearing = round(bearing_deg)

    return rounded_bearing





# 找方向角,模板匹配 ——————————————————
model_image = cv2.imread('90.jpg', 0)
search_image = cv2.imread('12345.jpg', 0)
match_points = RotationMatch(model_image, search_image)
print('匹配的最优区域的起点坐标为：', match_points['point'])
print('相对旋转角度为：', match_points['angle'])

draw_result(search_image, model_image, match_points['point'])


















