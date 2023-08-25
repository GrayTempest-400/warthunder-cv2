import requests
import math
from PIL import Image, ImageGrab
import time
from key_input.press_key import InputKey
from key_input import Keyboard
import ctypes
from find import find
from UI import init

input_key = InputKey(0)
box1 = find('pic/0.png', 0.8)
center_point = 'center_point'
ranging_speed = 'ranging_speed'
show = 'show'
size = 'size'
size_point = 'size_point'
speed_w = 'speed_w'


# 这是爬战区的
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
                    print(f"x{i + 1}: {x}")
                    print(f"y{i + 1}: {y}")

                if len(capture_zones) == 2:
                    # 获取玩家位置和朝向
                    x, y, dx, dy = get_Player()
                    ax, ay = capture_zones[0]["x"], capture_zones[0]["y"]
                    bx, by = capture_zones[1]["x"], capture_zones[1]["y"]

                    distance_a = math.sqrt((ax - x) ** 2 + (ay - y) ** 2)
                    distance_b = math.sqrt((bx - x) ** 2 + (by - y) ** 2)

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
                        return cx, cy
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
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def base():
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
            base = []
            for obj in data:
                if obj.get("type") == "respawn_base_tank" and obj.get("color") == "#7d00FA":
                    x = obj.get("x")
                    y = obj.get("y")
                    base.append({"x": x, "y": y})

            # 打印搜索结果
            if len(base) > 0:
                print("找到基地:")
                for i, zone in enumerate(base):
                    x = zone["x"]
                    y = zone["y"]
                    print(f"x{i + 1}: {x}")
                    print(f"y{i + 1}: {y}")

                    # 获取玩家位置和朝向
                    px, py, dx, dy = get_Player()

                    # 计算玩家与基地之间的距离
                    distance = calculate_distance(px, py, x, y)
                    print(f"到敌方基地 {i + 1} 的距离: {distance}")

                    # 记录最近的基地
                    if i == 0 or distance < nearest_distance:
                        nearest_base = {"x": x, "y": y}
                        nearest_distance = distance

                print("最近的敌方基地:")
                print(f"x: {nearest_base['x']}")
                print(f"y: {nearest_base['y']}")
                return x,y
            else:
                print("在 JSON 列表中未找到基地。")
        else:
            print("无效的 JSON 数据格式：预期是一个非空列表。")
    else:
        print("无法从 URL 检索数据。")

    return None
###################################################################
def check_vector_pointing(x, y, dx, dy, ax, ay):  # 这是获取车辆和对目标点的向量的，ax,ay可传入自定义路径点
    dx_AB = ax - x
    dy_AB = ay - y

    dot_product = dx * dx_AB + dy * dy_AB

    angle = math.degrees(math.acos(dot_product / (math.sqrt(dx ** 2 + dy ** 2) * math.sqrt(dx_AB ** 2 + dy_AB ** 2))))
    distance_to_target = math.sqrt((ax - x) ** 2 + (ay - y) ** 2)
    if distance_to_target < 0.005:
        return True
    if dot_product > 0 and math.isclose(angle, 0, abs_tol=1e-6):
        return "Go straight"
    elif angle <= 5:
        input_key.click_key(Keyboard.W, 3)  # input_key.click_key(Keyboard.W, 3)中的3是按键秒数，可自行调整
        return "Go straight"
    else:
        angle_diff = math.atan2(dy, dx) - math.atan2(ay - y, ax - x)
        if angle_diff < 0:
            input_key.click_key(Keyboard.D, 0.5)  # input_key.click_key(Keyboard.D, 1)1是按键秒数，可自行调整
            return "Turn right"

        else:
            input_key.click_key(Keyboard.A, 0.8)  # input_key.click_key(Keyboard.D, 1)1是按键秒数，可自行调整
            return "Turn left"

####################################################################################################
def ocr_digit(image_path):
    # 打开图像
    image = Image.open(image_path)

    # 使用Tesseract进行OCR识别
    text = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

    # 返回识别的数字文本
    return text.strip()



def speed_detect():
    speed_list = []  # 存储速度的列表
    consecutive_below_one = 0  # 连续小于1的计数器
    box1 = find('pic/0.png',0.8)
    while True:
        if box1 is None:
            print("速度控制停止")
            break
        try:
            time.sleep(1)
            img = ImageGrab.grab(init[speed_w])  # 速度存在位置的坐标
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
                if box1 is None:
                    print("速度控制停止")
                    break
                print({"速度": speed})
                if box1 is None:
                    print("速度控制停止")
                    break

                if speed < 3:  # 当速度小于3开始计
                    consecutive_below_one += 1
                else:
                    consecutive_below_one = 0

                if consecutive_below_one >= 5:
                    print("遇到障碍")
                    ctypes.windll.kernel32.Beep(1000, 50)
                    input_key.click_key(Keyboard.S, 3)  # 自定义障碍处理
                    input_key.click_key(Keyboard.D, 5)
                    input_key.click_key(Keyboard.W, 5)

                    consecutive_below_one = 0

                if len(speed_list) > 120:
                    speed_list = []  # 清空速度列表
        except:
            if box1 is None:
                print("速度控制停止")
                break

            print("获取速度失败")

        print(recognized_text)


###########################################################################
import pytesseract
import multiprocessing
from findway.way import way


def capture_image():
    image = ImageGrab.grab((0, 0, 305, 37))
    return image


def press_m_key():
    input_key.click_key(Keyboard.M, 5)  # Assuming input_key and Keyboard are defined somewhere


def main():
    # Create processes for image capture and key press
    image_process = multiprocessing.Process(target=capture_image)
    key_process = multiprocessing.Process(target=press_m_key)

    # Start both processes
    image_process.start()
    key_process.start()

    # Wait for both processes to finish
    image_process.join()
    key_process.join()

    # Now you can perform OCR and further processing
    image = image_process.result()  # Get the captured image
    ocr_result = pytesseract.image_to_string(image, lang='cn')
    map_name = ocr_result.strip()  # Remove leading/trailing whitespace

    # Define a dictionary mapping map names to JSON positions
    map_json_positions = {
        "地图名1": "json位置1",
        "地图名2": "json位置2",
        "地图名3": "json位置3",
        # Add more mappings as needed
    }

    if map_name in map_json_positions:
        way(map_json_positions[map_name])  # Use the corresponding JSON position
    else:
        print("Map not found in dictionary")
    ###########################################################################


def find_way():
    while True:
        if box1 is None:
            print("寻路控制停止")
            break
        get_capture_zone()
        get_Player()
        x, y, dx, dy = get_Player()

        xx, xy = get_capture_zone()
        bx, by = base()
        print("正在向战区行驶")
        b = check_vector_pointing(x, y, dx, dy, xx, xy)  # xx,xy可更换为自定义路径点如（0.123456,0.114514)
        print("停止15秒来占点")
        time.sleep(15)
        if b :
            print("正在向敌方出生点行驶")
            check_vector_pointing(x, y, dx, dy, bx, by)



from edge_detect_range import loop
import multiprocessing


def run():
    processes = []

    def restart_p1():
        nonlocal p1
        p1.terminate()
        p1 = multiprocessing.Process(target=find_way)
        processes[0] = p1
        p1.start()

    p1 = multiprocessing.Process(target=find_way)
    processes.append(p1)
    p2 = multiprocessing.Process(target=speed_detect)
    processes.append(p2)
    p3 = multiprocessing.Process(target=loop)
    processes.append(p3)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    while True:
        print("box1", box1)
        if box1 is None:
            print("局内控制停止")
            for process in processes:
                process.terminate()
            break
        try:
            p1.join(timeout=1)  # Check if p1 has finished
        except multiprocessing.TimeoutError:
            print("find_way function is taking too long, restarting...")
            restart_p1()

    return True

if __name__ == '__main__':
    run()
