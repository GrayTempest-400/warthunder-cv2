import cv2
import argparse


foc = 1990.0        # 镜头焦距
real_hight_person = 66.9   # 行人高度
detect_distance_car = 57.08      # 轿车高度

# 自定义函数，单目测距
def detect_distance_person(h):
    dis_inch = (real_hight_person * foc) / (h - 2)
    dis_cm = dis_inch * 2.54
    dis_cm = int(dis_cm)
    dis_m = dis_cm / 100
    return dis_m

# 自定义函数，改变显示图片大小
def cv_show(p, im0):
    height, width = im0.shape[:2]
    a = 1200 / width  # 宽为1200，计算比例
    size = (1200, int(height * a))
    img_resize = cv2.resize(im0, size, interpolation=cv2.INTER_AREA)
    cv2.imshow(p, img_resize)
    cv2.waitKey(1)  # 1 millisecond

# 自定义函数，绘制带标签的框
def plot_one_box(x, img, color=None, label=None, line_thickness=3, name=None):
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))  # 传过来的x包含有框的两个对角坐标
    h = int(x[3]) - int(x[1])  # 框的高
    dis_m = 1.00
    if name == 'person':  # 根据标签名称调用不同函数计算距离
        dis_m = detect_distance_person(h)
    elif name == 'car':
        dis_m = detect_distance_car(h)
    label += f'  {dis_m}m'  # 在标签后追加距离
    cv2.rectangle(img, c1, c2, color, thickness=line_thickness, lineType=cv2.LINE_AA)
    tf = max(line_thickness - 1, 1)  # font thickness
    t_size = cv2.getTextSize(label, 0, fontScale=line_thickness / 3, thickness=tf)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
    cv2.putText(img, label, (c1[0], c1[1] - 2), 0, line_thickness / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

# 解析命令行参数
parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('--nosave', action='store_false', help='do not save images/videos')
args = parser.parse_args()

# 示例代码中的一部分，用于处理框的坐标和标签
conf2 = 0.8  # 示例中的置信度值
xyxy = [10, 20, 100, 200]  # 示例中的框坐标
label = 'person'  # 示例中的标签
cls = 0  # 示例中的类别索引
colors = [(255, 0, 0)]  # 示例中的颜色列表
names = ['person']  # 示例中的标签名称列表
im0 = cv2.imread('person.jpg')  # 示例中的图像

if conf2 > 0.4:  # 置信度小于0.4时不显示
    # person，显示person标签的框，并单独做person的测距
    if names[int(cls)] == 'person':
        plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3, name=names[int(cls)])  # 画框函数
while True:
   if args.nosave:
    cv_show('image', im0)
    k = cv2.waitKey(1)  # 0:不自动销毁也不会更新, 1:1ms延迟销毁
    if k % 256 == 27:
        cv2.destroyAllWindows()
        exit('ESC ...')


