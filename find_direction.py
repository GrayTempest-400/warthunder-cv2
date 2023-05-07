import cv2
import math
import numpy as np
#查找箭头的轮廓并计算其方向
#将图像转换为灰度图像。
#对灰度图像进行二值化处理。
#找到二值化图像中的轮廓。
#对每个轮廓进行逼近，以减少轮廓中的点数。
#如果逼近后的轮廓有7个点，则将其作为箭头的轮廓。
#找到箭头轮廓的边界框。
#将边界框中的区域提取出来，并将其转换为灰度图像。
#对提取出来的灰度图像进行二值化处理。
#找到二值化图像中的轮廓。
#对每个轮廓进行逼近，以减少轮廓中的点数。
#如果逼近后的轮廓有4个点，则将其作为箭头尖端的轮廓。
#找到箭头尖端轮廓的边界框。
#如果箭头尖端在图像中心附近，则计算箭头方向与水平方向之间的角度。
def get_arrow_direction(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True),True)
        if len(approx) == 7:
            x,y,w,h = cv2.boundingRect(cnt)
            roi = image[y:y+h,x:x+w]
            gray_roi = cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
            _,thresh_roi = cv2.threshold(gray_roi,127,255,cv2.THRESH_BINARY)
            contours_roi,_ = cv2.findContours(thresh_roi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            for cnt_roi in contours_roi:
                approx_roi = cv2.approxPolyDP(cnt_roi,0.01*cv2.arcLength(cnt_roi,True),True)
                if len(approx_roi) == 4:
                    x1,y1,w1,h1 = cv2.boundingRect(cnt_roi)
                    if x1 > w/3 and x1 < w*2/3 and y1 > h/3 and y1 < h*2/3:
                        angle = get_angle(x+w/2,y+h/2,x+x1+w1/2,y+y1+h1/2)
                        return angle

#计算两点之间的角度
def get_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    rads = math.atan2(-dy,dx)
    rads %= 2*math.pi
    degs = math.degrees(rads)
    return degs


#计算箭头是否指向点
def detect_arrow_direction(point1, point2, arrow_point):
    # 计算两点之间的角度
    angle = np.arctan2(point2[1] - point1[1], point2[0] - point1[0]) * 180 / np.pi

    # 计算箭头点和第二个点之间的角度
    arrow_angle = np.arctan2(arrow_point[1] - point2[1], arrow_point[0] - point2[0]) * 180 / np.pi

    # 计算两个角度之间的差异
    angle_diff = abs(angle - arrow_angle)

    # 如果差异小于10度，则箭头指向第二个点
    if angle_diff < 10:
        return True
    else:
        return False

# 示例用法
point1 = (10, 10)
point2 = (50, 50)
arrow_point = (30, 30)

if detect_arrow_direction(point1, point2, arrow_point):
    print("箭头指向第二个点")
else:
    print("箭头未指向第二个点")


#get_arrow_direction，它使用Canny边缘检测和霍夫变换来检测箭头并确定其方向。在这个示例中，我们将图像文件arrow.png传递给get_arrow_direction函数，并打印出箭头的方向。
def get_direction(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return None

    for line in lines:
        rho, theta = line[0]
        if np.pi / 4 <= theta <= 3 * np.pi / 4:
            return "up" if rho < 0 else "down"
        else:
            return "left" if rho < 0 else "right"
#is_arrow_pointing_to_coordinate函数使用get_arrow_direction函数来获取箭头的方向，并使用数学计算来确定箭头是否指向一个坐标。
# 在这个示例中，我们将图像文件arrow.png传递给is_arrow_pointing_to_coordinate函数，并传递坐标(100,100)，以确定箭头是否指向该坐标
def is_arrow_pointing_to_coordinate(img, x, y):
    arrow_direction = get_arrow_direction(img)

    if arrow_direction == "up":
        return y < img.shape[0] / 2
    elif arrow_direction == "down":
        return y > img.shape[0] / 2
    elif arrow_direction == "left":
        return x < img.shape[1] / 2
    elif arrow_direction == "right":
        return x > img.shape[1] / 2

img = cv2.imread("arrow.png")
is_pointing_to_coordinate = is_arrow_pointing_to_coordinate(img, 100, 100)
print(is_pointing_to_coordinate)

