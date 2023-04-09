import os
import cv2
import pandas as pd

path = 'have_thank'  # 坦克数据集正样本的路径
filelist = os.listdir(path)
count = 1000  # 开始文件名1000.jpg
for file in filelist:
    Olddir = os.path.join(path, file)
    if os.path.isdir(Olddir):
        continue
    filename = os.path.splitext(file)[0]
    filetype = os.path.splitext(file)[1]
    Newdir = os.path.join(path, str(count) + filetype)
    os.rename(Olddir, Newdir)
    count += 1



for n in range(10000, 11790):  # 代表正数据集中开始和结束照片的数字
    path = 'have_thank' + str(n) + '.jpg'
    # 读取图片
    img = cv2.imread(path)
    img = cv2.resize(img, (80, 80))  # 修改样本像素为20x20
    cv2.imwrite('have_thank' + str(n) + '.jpg', img)
    n += 1
