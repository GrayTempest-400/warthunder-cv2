import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from tqdm import trange

# 亮点绘制（地形图，坐标，半径，亮度，衰减方式）
def pointmaker(topography, coord, radius, luminance=255, decline=None):
    if decline is None:
        def decline(x):
            coef = radius**2 / np.log(luminance)
            return np.exp(-(x**2)/coef)
    for i in range(topography.shape[0]):
        for j in range(topography.shape[1]):
            dis = ((coord[0] - i)**2 + (coord[1] - j)**2)**0.5
            if dis <= radius:
                topography[i, j] += int(luminance * decline(dis))
#代价扩散（地形图，起点）
def cost_spread(topography, start):
    direction = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
    # 可行方向为周围8个方向，优先上下左右
    cost_map = np.zeros_like(topography, dtype=np.uint) - 1	# 代价图，初始化为uint的最大值
    cost_map[start] = topography[start]	# 更新起点代价
    backtrack_map = np.zeros((topography.shape[0], topography.shape[1], 2), dtype=np.uint)	# 回溯图，记录回溯坐标
    points = [start]	# 更新点队列
    while points:
        x, y = points.pop(0)
        neighbor = filter(lambda p: 0 <= p[0] < topography.shape[0] and 0 <= p[1] < topography.shape[1],
                          ((x + i, y + j) for i, j in direction))	# 邻点迭代器
        for point in neighbor:	# 更新所有邻点
            if cost_map[x, y] + topography[point] < cost_map[point]:
                cost_map[point] = cost_map[x, y] + topography[point]	# 更新代价图
                backtrack_map[point] = x, y	# 更新回溯图
                points.append(point)	# 加入更新点队列
    return backtrack_map
# 多路径绘制（地形图，起点，终点列表）
def pathfinding(topography, start, end_list):
    if type(end_list) != list:
        end_list = [end_list]
    color_map = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=len(end_list) - 1),
                                  cmap=plt.get_cmap('gist_rainbow'))
    backtrack_map = cost_spread(topography, start)
    plt.figure(figsize=(topography.shape[1]/5, topography.shape[0]/5))
    plt.imshow(topography, cmap='gray')
    for i in trange(len(end_list)-1, -1, -1):
        x, y = end_list[i]
        color = color_map.to_rgba(i)
        plt.scatter(y, x, color=color, marker='d')
        while True:
            if (x, y) == start:
                break
            last_x, last_y = backtrack_map[x, y]
            plt.plot((y, last_y), (x, last_x), color=color, linewidth=3)
            x, y = last_x, last_y
    plt.scatter(start[1], start[0], color=color_map.to_rgba(0))
    plt.savefig('path.png')
    # plt.show()

# 全路径绘制（地形图，起点）
# 相较于多路径绘制大幅度优化了绘制速度
def allpathfinding(topography, start):
    end_list = [(i, j) for i in range(topography.shape[0]) for j in range(topography.shape[1])]
    end_list.reverse()
    color_map = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=len(end_list)-1),
                                  cmap=plt.get_cmap('gist_rainbow'))
    backtrack_map = cost_spread(topography, start)
    plt.figure(figsize=(topography.shape[1]/5, topography.shape[0]/5))
    plt.imshow(topography, cmap='gray')
    while end_list:
        print(len(end_list))
        x, y = end_list.pop()
        color = color_map.to_rgba(topography.shape[1]*x + y)
        while True:
            if (x, y) == start:
                break
            last_x, last_y = backtrack_map[x, y]
            plt.plot((y, last_y), (x, last_x), color=color, linewidth=2)
            x, y = last_x, last_y
            if (last_x, last_y) in end_list:
                end_list.remove((last_x, last_y))
            else:
                break
    plt.savefig('path.png')

'''
pointmaker(topography, coord, radius, luminance=255, decline=None)函数调用示例：
python
Copy code
# 创建一个地形图
topography = np.zeros((10, 10))

# 调用pointmaker函数来绘制亮点
coord = (5, 5)
radius = 3
luminance = 255
pointmaker(topography, coord, radius, luminance)

# 可以继续在地形图上绘制更多的亮点

# 显示地形图
plt.imshow(topography, cmap='gray')
plt.show()
cost_spread(topography, start)函数调用示例：
python
Copy code
# 创建一个地形图
topography = np.array([[1, 2, 3],
                       [4, 5, 6],
                       [7, 8, 9]])

# 设置起点
start = (0, 0)

# 调用cost_spread函数进行代价扩散
backtrack_map = cost_spread(topography, start)

# 输出代价扩散结果
print(backtrack_map)
pathfinding(topography, start, end_list)函数调用示例：
python
Copy code
# 创建一个地形图
topography = np.array([[1, 2, 3],
                       [4, 5, 6],
                       [7, 8, 9]])

# 设置起点和终点列表
start = (0, 0)
end_list = [(2, 2), (1, 1)]

# 调用pathfinding函数进行路径绘制
pathfinding(topography, start, end_list)
allpathfinding(topography, start)函数调用示例：
python
Copy code
# 创建一个地形图
topography = np.array([[1, 2, 3],
                       [4, 5, 6],
                       [7, 8, 9]])

# 设置起点
start = (0, 0)

# 调用allpathfinding函数进行全路径绘制
allpathfinding(topography, start)
以上示例代码可以根据你的具体需求进行调整和修改。确保提供正确的参数和输入数据，以便函数能够正确执行和产生期望的结果。'''


#代码参考https://blog.csdn.net/Eyizoha/article/details/89644230
