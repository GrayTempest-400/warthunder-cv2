import cv2
import numpy as np
import math

img =cv2.imread("jt.jpg")

def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)           #进行高斯滤波
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)           #二值化，使得图片更加清晰没有中间模糊的像素点
    ret,img_thr = cv2.threshold(img_blur,70,255,cv2.THRESH_BINARY)
    img_canny = cv2.Canny(img_thr, 50, 50)##边缘检测
    kernel = np.ones((3, 3),np.uint8)
    img_dilate = cv2.dilate(img_canny, kernel, iterations =2)#边缘膨胀膨胀
    img_erode = cv2.erode(img_dilate, kernel, iterations =1)#边缘腐蚀腐蚀
    return img_erode
##寻找箭头顶点和底点用于计算方向
def find_tip(points, convex_hull):
    length = len(points)
    indices = np.setdiff1d(range(length), convex_hull)#寻找箭头内凹的两个点的索引
    for i in range(2):
        j = indices[i] + 2
        if j > length - 1:
            j = length -j
        p = j + 2
        if p > length - 1:
            p = length -p
        if np.all(points[j] == points[indices[i-1]-2]):
            return tuple([points[j],points[p]])
'''将箭头顶点坐标旋转45度，通过旋转坐标，可以通过判断在坐标轴的哪个象限就可以知道箭头方向了'''
def rotate(angle,xy):
    rotatex = math.cos(angle)*xy[0] -math.sin(angle)*xy[1]
    rotatey = math.cos(angle)*xy[0] + math.sin(angle)*xy[1]
    return(tuple([rotatex,rotatey]))

contours, hierarchy = cv2.findContours(preprocess(img), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

for cnt in contours:
    peri = cv2.arcLength(cnt, True)##获取周长
    approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)#获取端点，会返回轮廓的多边形端点值
    hull = cv2.convexHull(approx, returnPoints=False)#获取凸包,返回凸包角点的索引，注意本项目是针对端点多边形获取凸包，所以如果是箭头，则箭头里面的两个端点会被忽略
    print(hull)
    sides = len(hull)            #判断箭头的依据是图像的端点个数比凸包少2个点即可

    if 6 > sides > 3 and sides + 2 == len(approx):     #if 5 > sides > 3 and sides == len(approx):
        arrow_tip = find_tip(approx[:,0,:], hull.squeeze())


        if arrow_tip:
            arrow_dir = np.array(arrow_tip[0]) - np.array(arrow_tip[1])
            arrow_rotate= rotate(math.pi/4,arrow_dir)

            if arrow_rotate[0] > 0:
                if arrow_rotate[1] > 0:
                    print("箭头向右")
                else:
                    print("箭头向上")
            else:
                if arrow_rotate[1] > 0:
                    print("箭头向下")
                else:
                    print("箭头向左")

print("箭头旋转角度为：", arrow_rotate[1]+arrow_rotate[0]-4.242640687119287)

