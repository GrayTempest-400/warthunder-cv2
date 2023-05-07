import ctypes
import os
import time
import pyautogui
import win32con
import win32gui
from loguru import logger
import dearpygui.dearpygui as dpg
from find import locate

logger.remove(handler_id=None)
logger.add("wtauto_{time:YYYY-MM-DD}.log", format='{time:YYYY-MM-DD HH:mm} {level} {message}', rotation='3 days',
           encoding='UTF-8')


def active():  # 窗口置顶
    global hwnd
    hwnd = win32gui.FindWindow('DagorWClass', None)
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    win32gui.SetForegroundWindow(hwnd)


def click(p):  # 第二种
    hwnd = win32gui.FindWindow('DagorWClass', None)
    win32gui.SetForegroundWindow(hwnd)
    x = p[0]
    y = p[1]
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.1)
    pyautogui.moveTo(x=20, y=300)


def checklog(param):
    out = param + '\n'
    with open('pic/check/check.ini', 'r+') as check:
        check.seek(0, 2)
        check.write(out)


def logger_log(param):
    try:
        logger.info(param)
        checklog(param)
        print(param)
    except:
        logger.exception("日志异常")


def coun(name):  # 读取本地有没有country文件，判断选择哪个国家
    c = os.path.exists('pic/config/country.txt')
    if c is True:
        with open('pic/config/country.txt', 'w+') as country:
            country.seek(0, 0)
            co = country.readlines()
            if co == name:
                return co
            else:
                country.truncate(0)
                country.write(name)
                co = country.readlines()
                return co
    else:
        with open('pic/config/country.txt', 'w+') as country:
            country.seek(0, 0)
            country.write(name)
            co = country.readlines()
            return co


def us():
    coun('us')
    dpg.delete_item(item='modal_id')
    logger_log('选择美国')


def ger():
    coun('ger')
    dpg.delete_item(item='modal_id')
    logger_log('选择德国')


def ussr():
    coun('ussr')
    dpg.delete_item(item='modal_id')
    logger_log('选择苏联')


def uk():
    coun('uk')
    dpg.delete_item(item='modal_id')
    logger_log('选择英国')


def jp():
    coun('jp')
    dpg.delete_item(item='modal_id')
    logger_log('选择日本')


def it():
    coun('it')
    dpg.delete_item(item='modal_id')
    logger_log('选择意呆')


def selectrun():  # 判断运行哪一个版本游戏
    st = os.path.exists('pic/config/steam.d')
    gj = os.path.exists('pic/config/gaijin.d')
    if st is True:
        logger_log('运行steam版')
        return 1
    elif gj is True:
        logger_log('运行Gaijin版')
        return 2


def selet_c():  # 选择国家
    hwnd = win32gui.FindWindow('DagorWClass', None)
    if not hwnd == 0:
        se = os.path.exists('pic/config/country.txt')
        print(se)
        if se is True:
            with open('pic/config/country.txt', 'r') as country:
                co = country.readline()
                print(co)
            if co == 'us':
                c = locate('pic/country/usa.png', 0.8)
                time.sleep(0.5)
                click(c)
                time.sleep(1)
                s = locate('pic/luncher/hang.png', 0.8)
                click(s)
                logger_log('选择完毕')
            elif co == 'ger':
                c = locate('pic/country/ger.png', 0.8)
                time.sleep(0.5)
                click(c)
                time.sleep(1)
                s = locate('pic/luncher/hang.png', 0.8)
                click(s)
                logger_log('选择完毕')
            elif co == 'ussr':
                c = locate('pic/country/ussr.png', 0.8)
                time.sleep(0.5)
                click(c)
                time.sleep(1)
                s = locate('pic/luncher/hang.png', 0.8)
                click(s)
                logger_log('选择完毕')
            elif co == 'uk':
                c = locate('pic/country/uk.png', 0.8)
                time.sleep(0.5)
                click(c)
                time.sleep(1)
                s = locate('pic/luncher/hang.png', 0.8)
                click(s)
                logger_log('选择完毕')
            elif co == 'jp':
                c = locate('pic/country/jp.png', 0.8)
                time.sleep(0.5)
                click(c)
                time.sleep(1)
                s = locate('pic/luncher/hang.png', 0.8)
                click(s)
                logger_log('选择完毕')
            elif co == 'it':
                c = locate('pic/country/it.png', 0.8)
                time.sleep(0.5)
                click(c)
                time.sleep(1)
                s = locate('pic/luncher/hang.png', 0.8)
                click(s)
                logger_log('选择完毕')
            else:
                a = False
                return a
        else:
            a = False
            return a
