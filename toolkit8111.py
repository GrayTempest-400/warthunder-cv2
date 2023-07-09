import requests
import math
import pytesseract
from PIL import Image,ImageGrab
import time



#这是爬战区的
def get_capture_zone():
    url = "http://127.0.0.1:8111/map_obj.json"

    # 发送 GET 请求并获取响应
    response = requests.get(url)

    # 检查响应状态码，200 表示请求成功
    if response.status_code == 200:
        # 解析 JSON 响应
        data = response.json()

        # 确认数据是一个列表
        if isinstance(data, list) and len(data) > 0:
            # 搜索并提取符合条件的对象的 x 和 y 值
            capture_zones = []
            for obj in data:
                if obj.get("type") == "capture_zone":
                    x = obj.get("x")
                    y = obj.get("y")
                    capture_zones.append({"x": x, "y": y})

            # 打印搜索结果
            if len(capture_zones) > 0:
                print("Found capture zones:")
                for i, zone in enumerate(capture_zones):
                    if i == 0:
                        ax, ay = zone["x"], zone["y"]
                        print("ax:", ax)
                        print("ay:", ay)
                    elif i == 1:
                        bx, by = zone["x"], zone["y"]
                        print("bx:", bx)
                        print("by:", by)
                    elif i == 2:
                        cx, cy = zone["x"], zone["y"]
                        print("cx:", cx)
                        print("cy:", cy)
                    elif i == 3:
                        dx, dy = zone["x"], zone["y"]
                        print("dx:", dx)
                        print("dy:", dy)
                    print()
                # 返回结果
                if "cx" in locals() and "cy" in locals():
                    return ax, ay, bx, by, cx, cy
                elif "bx" in locals() and "by" in locals():
                    return ax, ay, bx, by
                elif "dx" in locals() and "dy" in locals():
                    return ax, ay, bx, by, cx, cy,dx,dy
                else:
                    return ax, ay


    # 如果没有找到capture_zones的cxcy，则返回ax, ay和bx, by的结果
    #如果没有找到capture_zones的bxby，则返回ax, ay的结果
    return None



#####################################################################################



def get_Player():
    #这是爬自己位置和车体朝向的，xy位置，dxdy朝向
    url = "http://127.0.0.1:8111/map_obj.json"

    # 发送 GET 请求并获取响应
    response = requests.get(url)

    # 检查响应状态码，200 表示请求成功
    if response.status_code == 200:
        # 解析 JSON 响应
        data = response.json()

        # 确认数据是一个列表
        if isinstance(data, list) and len(data) > 0:
            # 搜索并提取符合条件的对象的 x 和 y 值
            player_objects = []
            for obj in data:
                if obj.get("icon") == "Player":
                    x = obj.get("x")
                    y = obj.get("y")
                    dx = obj.get("dx")
                    dy = obj.get("dy")
                    player_objects.append({"x": x, "y": y , "dx": dx, "dy": dy})



            for player_obj in player_objects:
                x = player_obj["x"]
                y = player_obj["y"]
                dx = player_obj["dx"]
                dy = player_obj["dy"]
                statement = f" x={x} and y={y} and dx={dx} and dy={dy}"


            # 打印搜索结果
            if len(statement) > 0:


                print(statement)


    return x,y,dx,dy

###############################################################################################################


def check_vector_pointing(x, y, dx, dy, ax, ay):
    dx_AB = ax - x
    dy_AB = ay - y

    dot_product = dx * dx_AB + dy * dy_AB

    angle = math.degrees(math.acos(dot_product / (math.sqrt(dx**2 + dy**2) * math.sqrt(dx_AB**2 + dy_AB**2))))

    if dot_product > 0 and math.isclose(angle, 0, abs_tol=1e-6):
        return True
    elif angle <= 5:
        return "Go straight"
    else:
        angle_diff = math.atan2(dy, dx) - math.atan2(ay - y, ax - x)
        if angle_diff < 0:
            return "Turn right"

        else:
            return "Turn left"



def ocr_digit(image_path):
    # 打开图像
    image = Image.open(image_path)

    # 使用Tesseract进行OCR识别
    text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

    # 返回识别的数字文本
    return text.strip()
###########################################################################

import pygetwindow as gw

#初始化
# 查找名为'war thunder'的窗口
window = gw.getWindowsWithTitle('War Thunder')[0]

# 将窗口调整为1280x720
window.resizeTo(1280, 720)   #有的笔记本用户需将缩放调为100%，有的125%也能跑，这是玄学

# 将窗口移动到左上角
window.moveTo(0, 0)

# 获取窗口左下角的位置
window_left_bottom = (window.left, window.bottom)
print(window_left_bottom)
while True:
    time.sleep(5)
    get_capture_zone()
    get_Player()
    x, y, dx, dy = get_Player()
    ax, ay,bx,by,cx,cy= get_capture_zone()#这里纯纯是面向答案搞得，假如有A,B两个点就ax, ay,bx,by ，假如只有A就ax,ay  假如ABC就ax,ay,bx,by,cx,cy
    check_vector_pointing(x, y, dx, dy, ax, ay) #同理，找a点就check_vector_pointing(x, y, dx, dy, ax, ay)，找b就check_vector_pointing(x, y, dx, dy, bx, by)
    print( check_vector_pointing(x, y, dx, dy, ax, ay))
    try:
        img = ImageGrab.grab((47, 686, 100, 702))  # 速度存在位置的坐标
        img.save('speeds.png')
        recognized_text = ocr_digit('speeds.png')
        if len(recognized_text) == 2:
            speed = recognized_text[0] + recognized_text[1]
        elif len(recognized_text) == 3:
            speed = recognized_text[0] + recognized_text[1] + recognized_text[2]
        elif len(recognized_text) == 0:
            speed = None
        elif len(recognized_text) == 1:
            speed = recognized_text[0]
        print({"速度": speed})
        if speed == 0 and time.time > 5:         # 189-190 这两段不知道为什么跑不了
            print("遇到障碍")
    except:
        print("获取速度失败")
    print(recognized_text)




