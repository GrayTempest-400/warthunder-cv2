from detect import *
import time
import cv2
from win32gui import FindWindow, SetWindowPos
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE




show = 'show'
size = 'size'
init = {
    show: True,  # 显示, Down
    size: 200,  # 截图的尺寸, 屏幕中心截图周围大小
}

c = cx_cy()

text = 'Realtime Screen Capture Detect'

def loop():
    while True:

        t1 = time.perf_counter_ns()
        img = capture_screen_around_center(init[size]) # 如果句柄截图是黑色, 不能正常使用, 可以使用本行的截图方法
        t2 = time.perf_counter_ns()
        target , image= find_specific_purple_edges('detect.jpg' ,show = init[show])
        x, y = target
        t3 = time.perf_counter_ns()
        aim = get_coordinate(init[size], x, y)    #转换屏幕坐标
        print(aim)

        # 瞄点划线
        if aim:
            cv2.line(image, aim, (c[0], c[1]), (255, 255, 0), 2)
        # 展示图片
        cv2.namedWindow(text, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(text, image)
        SetWindowPos(FindWindow(None, text), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        cv2.waitKey(1)

if __name__ == "__main__":
    loop()