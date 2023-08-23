import math
import requests
import json

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
def check_vector_pointing(x, y, dx, dy, ax, ay):  # 这是获取车辆和对目标点的向量的，ax,ay可传入自定义路径点
    dx_AB = ax - x
    dy_AB = ay - y

    dot_product = dx * dx_AB + dy * dy_AB

    angle = math.degrees(math.acos(dot_product / (math.sqrt(dx ** 2 + dy ** 2) * math.sqrt(dx_AB ** 2 + dy_AB ** 2))))
    distance_to_target = math.sqrt((ax - x) ** 2 + (ay - y) ** 2)
    if distance_to_target < 0.005:
        return True
    if dot_product > 0 and math.isclose(angle, 0, abs_tol=1e-6):
        return None
    elif angle <= 5:
        #input_key.click_key(Keyboard.W, 3)  # input_key.click_key(Keyboard.W, 3)中的3是按键秒数，可自行调整
        print("Go straight")
    else:
        angle_diff = math.atan2(dy, dx) - math.atan2(ay - y, ax - x)
        if angle_diff < 0:
            #input_key.click_key(Keyboard.D, 1)  # input_key.click_key(Keyboard.D, 1)1是按键秒数，可自行调整
            print("Turn right")

        else:
            #input_key.click_key(Keyboard.A, 1)  # input_key.click_key(Keyboard.D, 1)1是按键秒数，可自行调整
            print( "Turn left")
import time


# 从 JSON 文件中读取数据
with open('player_data.json', 'r') as json_file:
    data_list = json.load(json_file)

current_index = 0  # 用于跟踪当前字典的索引
print("路径点总数为",len(data_list))
while current_index < len(data_list):
    time.sleep(1)
    print("读取数据")
    data = data_list[current_index]
    ax = data["x"]
    ay = data["y"]
    dx = data["dx"]
    dy = data["dy"]


    a = get_Player()
    result = check_vector_pointing(a[0], a[1], dx, dy, ax, ay)  # 将 x 和 y 作为 ax 和 ay 传入函数

    if result == True:
        current_index += 1  # 如果函数返回 True，前进到下一个字典
        print(f"已到达路径点{current_index}")
    else:
        continue  # 如果函数返回其他结果，继续循环
