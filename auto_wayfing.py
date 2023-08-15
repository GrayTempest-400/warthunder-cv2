import requests
import math
import pytesseract
from PIL import Image,ImageGrab
import time
import pygetwindow as gw
from key_input.press_key import InputKey
from key_input import Mouse, Keyboard
import threading
import ctypes

input_key = InputKey(0)

speed_w = 'speed_w'
init = {
    speed_w:(58, 1043, 81, 1065),#速度的坐标（左上角x,左上角y，右下角x,右下角y)
}
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
                    x = zone["x"]
                    y = zone["y"]
                    print(f"x{i+1}: {x}")
                    print(f"y{i+1}: {y}")
                    print()

                if len(capture_zones) == 2:
                    # 获取玩家位置和朝向
                    x, y, dx, dy = get_Player()
                    ax, ay = capture_zones[0]["x"], capture_zones[0]["y"]
                    bx, by = capture_zones[1]["x"], capture_zones[1]["y"]

                    distance_a = math.sqrt((ax - x)**2 + (ay - y)**2)
                    distance_b = math.sqrt((bx - x)**2 + (by - y)**2)

                    if distance_a < distance_b:
                        return ax, ay
                    else:
                        return bx, by
                elif len(capture_zones) == 1:
                    return capture_zones[0]["x"], capture_zones[0]["y"]
                elif len(capture_zones) == 3:
                    x, y, dx, dy = get_Player()
                    ax, ay = capture_zones[0]["x"], capture_zones[0]["y"]
                    bx, by = capture_zones[1]["x"], capture_zones[1]["y"]
                    cx, cy = capture_zones[2]["x"], capture_zones[2]["y"]
                    distance_a = math.sqrt((ax - x) ** 2 + (ay - y) ** 2)
                    distance_b = math.sqrt((bx - x) ** 2 + (by - y) ** 2)

                    if distance_a < distance_b:
                        return ax, ay
                    elif distance_a > distance_b:
                        return bx, by
                    else:
                        return cx ,cy
                else:
                    print("No capture zones found in the JSON list.")
            else:
                print("No capture zones found in the JSON list.")
        else:
            print("Invalid JSON data format: expected a non-empty list")
    else:
        print("Failed to retrieve data from the URL")

    return None




#####################################################################################



def get_Player():
    # 这是爬自己位置和车体朝向的，xy位置，dxdy朝向
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
                    player_objects.append({"x": x, "y": y, "dx": dx, "dy": dy})

            # 打印搜索结果
            if len(player_objects) > 0:
                player_obj = player_objects[0]  # Assuming there's only one player object
                x = player_obj["x"]
                y = player_obj["y"]
                dx = player_obj["dx"]
                dy = player_obj["dy"]
                statement = f"x={x} and y={y} and dx={dx} and dy={dy}"
                print(statement)

                return x, y, dx, dy

    return None


###############################################################################################################


def check_vector_pointing(x, y, dx, dy, ax, ay):          #这是获取车辆和对目标点的向量的，ax,ay可传入自定义路径点
    dx_AB = ax - x
    dy_AB = ay - y

    dot_product = dx * dx_AB + dy * dy_AB

    angle = math.degrees(math.acos(dot_product / (math.sqrt(dx**2 + dy**2) * math.sqrt(dx_AB**2 + dy_AB**2))))
    distance_to_target = math.sqrt((ax - x) ** 2 + (ay - y) ** 2)
    if distance_to_target < 0.0001:
        return None
    if dot_product > 0 and math.isclose(angle, 0, abs_tol=1e-6):
        return True
    elif angle <= 5:
        input_key.click_key(Keyboard.W, 3) #input_key.click_key(Keyboard.W, 3)中的3是按键秒数，可自行调整
        return "Go straight"
    else:
        angle_diff = math.atan2(dy, dx) - math.atan2(ay - y, ax - x)
        if angle_diff < 0:
            input_key.click_key(Keyboard.D, 1)#input_key.click_key(Keyboard.D, 1)1是按键秒数，可自行调整
            return "Turn right"

        else:
            input_key.click_key(Keyboard.A, 1)#input_key.click_key(Keyboard.D, 1)1是按键秒数，可自行调整
            return "Turn left"



def ocr_digit(image_path):
    # 打开图像
    image = Image.open(image_path)

    # 使用Tesseract进行OCR识别
    text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

    # 返回识别的数字文本
    return text.strip()
##################################################################################################################

def speed_detect():
    speed_list = []  # 存储速度的列表
    consecutive_below_one = 0  # 连续小于1的计数器
    while True:
        try:
            time.sleep(1)
            img = ImageGrab.grab(init[speed_w]) # 速度存在位置的坐标
            img.save('speeds.png')
            recognized_text = ocr_digit('speeds.png')
            if len(recognized_text) == 2:
                speed = int(recognized_text[0] + recognized_text[1])
            elif len(recognized_text) == 3:
                speed = int(recognized_text[0] + recognized_text[1] + recognized_text[2])
            elif len(recognized_text) == 1:
                speed = int(recognized_text[0])

            if speed is not None:
                speed_list.append(speed)
                print({"速度": speed})

                if speed < 3:           #当速度小于3开始计
                    consecutive_below_one += 1
                else:
                    consecutive_below_one = 0

                if consecutive_below_one >= 5:
                    print("遇到障碍")
                    ctypes.windll.kernel32.Beep(1000,50)
                    input_key.click_key(Keyboard.S, 5) #自定义障碍处理
                    input_key.click_key(Keyboard.D, 5)
                    input_key.click_key(Keyboard.W, 5)

                    consecutive_below_one = 0

                if len(speed_list) > 120:
                    speed_list = []  # 清空速度列表
        except:
            print("获取速度失败")

        print(recognized_text)


###########################################################################
import pytesseract
def find_map():
    input_key.click_key(Keyboard.M, 10)#按M键10秒
    image = ImageGrab.grab((0,0,305,37))
    ocr_result = pytesseract.image_to_string(image, lang='cn')
    map = []
    map.append(ocr_result)
    if map == "你的自定义点所在的地图":
        mx,my = 0.114,0.514#自定义路径点
        mx2,my2 = 0.114,0.514#自定义路径点 可以此类推
        get_capture_zone()
        get_Player()
        x, y, dx, dy = get_Player()
        check_vector_pointing(x, y, dx, dy, mx,my)
        check_vector_pointing(x, y, dx, dy, mx2, my2)
    ###########################################################################

def find_way():
    while True:


        get_capture_zone()
        get_Player()
        x, y, dx, dy = get_Player()

        xx, xy = get_capture_zone()

        check_vector_pointing(x, y, dx, dy, xx,xy)       #xx,xy可更换为自定义路径点如（0.123456,0.114514)


threads = []

t1 = threading.Thread(target=speed_detect)
threads.append(t1)
t2 = threading.Thread(target=find_way)
threads.append(t2)
if __name__=='__main__':
    for t in threads:
        t.start()
    for t in threads:
        t.join()
print ("退出线程")