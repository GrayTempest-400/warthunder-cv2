import time

import pyautogui

from find import find_match, find, locate, check
from utils import click, active,logger_log as log

llj = 'pic/llj.png'
Select_the_mode = llj #陆历join
def find_box():
    box1 = locate('pic/ok02.png', 0.8)
    box2 = locate('pic/ok03.png', 0.8)
    box3 = locate('pic/x.png', 0.8)
    box4 = locate('pic/close.png', 0.8)
    if box1 is not None:
        click(box1)
        time.sleep(0.1)
    elif box2 is not None:
        click(box2)
        time.sleep(0.1)
    elif box3 is not None:
        click(box3)
        time.sleep(0.1)
    elif box4 is not None:
        click(box4)
        time.sleep(0.1)

    else:
        log('未检测到错误情况')


def join():#加入游戏，并且判断是否加入
    global flag
    flag = False
    while True:
        active()
        join = locate('pic/join.png', 0.8)
        time.sleep(0.5)
        if join is not None:

            changetank = find('pic/tankteam.png')
            click(changetank)
            click(join)
            log('加入')
            time.sleep(0.1)
            checkjoin = check('pic/join.png', 0.8)
            checkship = check('pic/notank2.png', 0.7)

            if checkjoin is True or checkship is True:
                log('加入出现问题')
                try:
                    changetank = find('pic/tankteam.png')
                    click(changetank)

                    kj = locate('pic/mod1.png', 0.8)#空战街机
                    kl = locate('pic/mod2.png', 0.8)#空历
                    lj = locate('pic/mod3.png', 0.8)#陆街
                    hj = locate('pic/mod5.png', 0.8)#海街
                    hl = locate('pic/mod6.png', 0.8)#海历
                    mn = locate('pic/mod7.png',0.8)#全真
                    ksw = locate('pic/mod8.png',0.8)#空守卫
                    lsw = locate('pic/mod9.png',0.8)#陆守卫
                    ll = locate('pic/mod4.png',0.8)#陆历

                    if ll is not None:
                        click(ll)
                        time.sleep(0.1)
                    elif kj is not None:
                        click(kj)
                        time.sleep(0.1)
                    elif kl is not None:
                        click(kl)
                        time.sleep(0.1)
                    elif lj is not None:
                        click(lj)
                        time.sleep(0.1)
                    elif hj is not None:
                        click(hj)
                        time.sleep(0.1)
                    elif hl is not None:
                        click(hl)
                        time.sleep(0.1)
                    elif mn is not None:
                        click(mn)
                        time.sleep(0.1)
                    elif ksw is not None:
                        click(ksw)
                        time.sleep(0.1)
                    elif lsw is not None:
                        click(lsw)
                        time.sleep(0.1)

                    llj = locate(Select_the_mode, 0.8)#改需点击的模式
                    if llj is not None:
                        click(llj)
                        time.sleep(0.1)


                    ok02 = find('pic/ok02.png')
                    click(ok02)
                    ok03 = find('pic/ok03.png')
                    click(ok03)
                    if ok03 is None and ok02 is None:
                        raise TypeError
                except:
                    log('未检测到错误情况')
                    continue
                time.sleep(0.1)
            else:
                log('已经成功点击')

        else:
            log('正在加入，请稍后')
            find_box()
            join1 = locate('pic/join.png', 0.8)
            if join1 is not None:
                log('停止检测加入')
                break
        time.sleep(1)
        # print('=========================================================================')
        wait = locate('pic/time.png', 0.8)
        time.sleep(0.5)
        if wait is not None:
            pyautogui.moveTo(10,30)
            log('已经加入战局')
            return True


def joinship():#选择船只
    # print('============================================================')
    i1 = 0
    while True:
        i1 = i1 + 1
        active()
        tank = locate('pic/join.png', 0.7)
        print(tank)
        time.sleep(1)
        if tank is not None:
            print('点击加入')
            click(tank)
            time.sleep(0.1)
            return True
        elif i1 > 15:
            hvj = locate('pic/0.png', 0.8)
            noselectship = locate('pic/join.png', 0.8)

            if hvj is not None:
                log('游戏已经开始')
                return True

            elif noselectship is not None:
                flag_False = locate('pic/flag_false.png', 0.8)
                Respawnpoint = find_match('pic/Respawn point.png',0.8)
                if flag_False is not None:
                    log('未知错误')
                    return None
                elif flag_False is None:
                    log('未选择坦克')
                    return False

            else:
                log('未能成功加入')
                return False

        else:
            log('没有坦克可以加入')
            time.sleep(2)


def main_join():
    global Fg
    pic_list = ['pic/lost.png', 'pic/0.png', 'pic/time.png']
    for pic in pic_list:
        Fg = 0
        print(pic)
        j = locate(pic, 0.7)
        if j is not None and pic == 'pic/lost.png':
            log('在主菜单')
            Fg = 1
            break
        elif j is not None and pic == 'pic/0.png':
            log('游戏已经开始')
            Fg = 2
            break
        elif j is not None and pic == 'pic/time.png':
            log('尚未选择坦克')
            Fg = 3
            break
    if Fg == 1:
        join()
        time.sleep(0.5)
        j1 = joinship()
        if j1 is True:
            return True
        elif j1 is False:
            return False
    elif Fg == 2:
        return True
    elif Fg == 3:
        j1 = joinship()
        if j1 is True:
            return True
        elif j1 is False:
            return False
    elif Fg == 0:
        return False



