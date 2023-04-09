#您需要将“recognize”函数中的代码替换为使用cv2自己训练的名为thank.xlm的训练集识别
import win32gui
import win32ui
import win32con
import win32api
import cv2


def get_window_info():
    # 获取窗口句柄
    hwnd = win32gui.FindWindow(None, '窗口标题')
    # 获取窗口位置信息
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    # 获取设备上下文DC（Divice Context）
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    # 截图至位图对象
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    # 将位图对象保存至文件
    saveBitMap.SaveBitmapFile(saveDC, 'screenshot.bmp')


def recognize():
    img = cv2.imread('screenshot.bmp')
    # 使用cv2自己训练的名为thank.xlm的训练集识别


if __name__ == '__main__':
    get_window_info()
    recognize()



