from win32gui import FindWindow, SetWindowPos, GetWindowText, GetForegroundWindow
import time
while True:
    time.sleep(5)
    print(GetWindowText(GetForegroundWindow()))