# -*- coding: utf-8 -*-

import os, sys, random, math

#地图设置
gameMapWidth = 10
gameMapHeight = 10
gameMap = []

#地图障碍物
obstacleCount = 5

#块状态
ITEM_STAT_NORMAL = 0        #空点
ITEM_STAT_OBSTACLE = 1      #障碍物
ITEM_STAT_START = 2         #起点
ITEM_STAT_END = 3           #终点

#起点和终点
spNum = -1
epNum = -1

#每块的属性
class Item:
    def __init__(self, x, y, status):
        self.x = x
        self.y = y
        self.status = status
        self.mf = -1
        self.mg = -1
        self.mh = -1
        self.mParent = None
        self.isPath = 0

#初始化地图
def initMap():
    for wc in range(gameMapWidth):
        for hc in range(gameMapHeight):
            gameMap.append(Item(wc, hc, ITEM_STAT_NORMAL))

    #插入障碍物
    for oc in range(obstacleCount):
        choose = random.randint(gameMapWidth, gameMapWidth * gameMapHeight - 1)
        gameMap[choose].status = ITEM_STAT_OBSTACLE

    global spNum
    global epNum
    #选取起点和终点
    while (spNum == -1):
        choose = random.randint(0, gameMapWidth * gameMapHeight - 1)
        if gameMap[choose].status == 0:
            spNum = choose
            gameMap[spNum].status = ITEM_STAT_START

    while (epNum == -1):
        choose = random.randint(0, gameMapWidth * gameMapHeight - 1)
        if gameMap[choose].status == 0:
            epNum = choose
            gameMap[epNum].status = ITEM_STAT_END

#输出地图信息
def printMap():
    for itemc in range(len(gameMap)):
        if gameMap[itemc].status == ITEM_STAT_START:
            print("START", end=" ")
        elif gameMap[itemc].status == ITEM_STAT_END:
            print("END", end=" ")
        elif gameMap[itemc].isPath == 1:
            print("path", end=" ")
        else:
            print("%d" %(gameMap[itemc].status), end=" ")

        if (itemc + 1) % gameMapHeight == 0:
            print("\n")

#寻路
def findPath():
    global spNum
    global epNum

    #开启列表
    openPointList = []
    #关闭列表
    closePointList = []

    #开启列表插入起始点
    openPointList.append(gameMap[spNum])
    while (len(openPointList) > 0):
        #寻找开启列表中最小预算值的点
        minFPoint = findPointWithMinF(openPointList)
        #从开启列表移除,添加到关闭列表
        openPointList.remove(minFPoint)
        closePointList.append(minFPoint)
        #找到当前点周围点
        surroundList = findSurroundPoint(minFPoint, closePointList)

        #开始寻路
        for sp in surroundList:
            #存在在开启列表，说明上一块查找时并不是最优路径，考虑此次移动是否是最优路径
            if sp in openPointList:
                newPathG = CalcG(sp, minFPoint) #计算新路径下的G值
                if newPathG < sp.mg:
                    sp.mg = newPathG
                    sp.mf = sp.mg + sp.mh
                    sp.mParent = minFPoint
            else:
                sp.mParent = minFPoint      #当前查找到点指向上一个节点
                CalcF(sp, gameMap[epNum])
                openPointList.append(sp)
        if gameMap[epNum] in openPointList:
            gameMap[epNum].mParent = minFPoint
            break

    curp = gameMap[epNum]
    while True:
        curp.isPath = 1
        curp = curp.mParent
        if curp == None:
            break
    print("\n")
    printMap()

def CalcG(point, minp):
    return math.sqrt((point.x - point.mParent.x)**2 + (point.y - point.mParent.y)**2) + minp.mg

#计算每个点的F值
def CalcF(point, endp):
    h = abs(endp.x - point.x) + abs(endp.y - point.y)
    g = 0
    if point.mParent == None:
        g = 0
    else:
        g = point.mParent.mg + math.sqrt((point.x - point.mParent.x)**2 + (point.y - point.mParent.y)**2)
    point.mg = g
    point.mh = h
    point.mf = g + h
    return

#不能是障碍块，不包含在关闭列表中
def notObstacleAndClose(point, closePointList):
    if point not in closePointList and point.status != ITEM_STAT_OBSTACLE:
        return True
    return False

#查找周围块
def findSurroundPoint(point, closePointList):
    surroundList = []
    up = None
    down = None
    left = None
    right = None

    leftUp = None
    rightUp = None
    leftDown = None
    rightDown = None

    #上面的点存在
    if point.x > 0:
        up = gameMap[gameMapHeight * (point.x - 1) + point.y]
        if notObstacleAndClose(up, closePointList):
            surroundList.append(up)
    #下面的点存在
    if point.x < gameMapWidth - 1:
        down = gameMap[gameMapHeight * (point.x + 1) + point.y]
        if notObstacleAndClose(down, closePointList):
            surroundList.append(down)
    #左边的点存在
    if point.y > 0:
        left = gameMap[gameMapHeight * (point.x) + point.y - 1]
        if notObstacleAndClose(left, closePointList):
            surroundList.append(left)
    #右边的点存在
    if point.y < gameMapHeight - 1:
        right = gameMap[gameMapHeight * (point.x) + point.y + 1]
        if notObstacleAndClose(right, closePointList):
            surroundList.append(right)
    #斜方向的点还需考虑对应正方向不是障碍物
    #左上角的点存在
    if point.x > 0 and point.y > 0:
        leftUp = gameMap[gameMapHeight * (point.x - 1) + point.y - 1]
        if (
            notObstacleAndClose(leftUp, closePointList)
            and left.status != ITEM_STAT_OBSTACLE
            and up.status != ITEM_STAT_OBSTACLE
        ):
            surroundList.append(leftUp)
    #右上角的点存在
    if point.x > 0 and point.y < gameMapHeight - 1:
        rightUp = gameMap[gameMapHeight * (point.x - 1) + point.y + 1]
        if (
            notObstacleAndClose(rightUp, closePointList)
            and right.status != ITEM_STAT_OBSTACLE
            and up.status != ITEM_STAT_OBSTACLE
        ):
            surroundList.append(rightUp)
    #左下角的点存在
    if point.x < gameMapWidth - 1 and point.y > 0:
        leftDown = gameMap[gameMapHeight * (point.x + 1) + point.y - 1]
        if (
            notObstacleAndClose(leftDown, closePointList)
            and left.status != ITEM_STAT_OBSTACLE
            and down.status != ITEM_STAT_OBSTACLE
        ):
            surroundList.append(leftDown)
    #右下角的点存在
    if point.x < gameMapWidth - 1 and point.y < gameMapHeight - 1:
        rightDown = gameMap[gameMapHeight * (point.x + 1) + point.y + 1]
        if (
            notObstacleAndClose(rightDown, closePointList)
            and right.status != ITEM_STAT_OBSTACLE
            and down.status != ITEM_STAT_OBSTACLE
        ):
            surroundList.append(rightDown)
    return surroundList

#查找list中最小的f值
def findPointWithMinF(openPointList):
    f = 0xffffff
    temp = None
    for pc in openPointList:
        if pc.mf < f:
            temp = pc
            f = pc.mf
    return temp


def main():
    initMap()  ##初始化地图
    printMap()  ##输出初始化地图信息
    findPath()  ##查找最优路径


#入口
main()
