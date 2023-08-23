import requests
import json
import tkinter as tk
from tkinter import messagebox

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

def record_player_data():
    player_data = get_Player()

    if player_data is not None:
        player_json = {
            "x": player_data[0],
            "y": player_data[1],
            "dx": player_data[2],
            "dy": player_data[3]
        }

        output_file_path = "player_data.json"

        player_data_list.append(player_json)  # Append new data to the list
        with open(output_file_path, "w") as json_file:
            json.dump(player_data_list, json_file, indent=4)
        print(f"Player data saved to {output_file_path}")
        messagebox.showinfo("Record Successful", "Player data saved!")

# Initialize the player data list
player_data_list = []

# Create a GUI window
root = tk.Tk()
root.title("Player Data Recorder")

# Create a "Record" button
record_button = tk.Button(root, text="Record", command=record_player_data)
record_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()