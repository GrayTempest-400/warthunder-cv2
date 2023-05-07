import time
from ctypes import POINTER, c_ulong, Structure, c_ushort, c_short, c_long, byref, windll, pointer, sizeof, Union

SendInput = windll.user32.SendInput
PUL = POINTER(c_ulong)


class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort), ("wScan", c_ushort), ("dwFlags", c_ulong),
                ("time", c_ulong), ("dwExtraInfo", PUL)]


class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong), ("wParamL", c_short), ("wParamH", c_ushort)]


class MouseInput(Structure):
    _fields_ = [("dx", c_long), ("dy", c_long), ("mouseData", c_ulong),
                ("dwFlags", c_ulong), ("time", c_ulong), ("dwExtraInfo", PUL)]


class Input_I(Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]


class Input(Structure):
    _fields_ = [("type", c_ulong), ("ii", Input_I)]


# Actuals Functions


def PressKey(hexKeyCode):
    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, pointer(extra))
    x = Input(c_ulong(1), ii_)
    windll.user32.SendInput(1, pointer(x), sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, pointer(extra))
    x = Input(c_ulong(1), ii_)
    windll.user32.SendInput(1, pointer(x), sizeof(x))

def press(k):
    PressKey(k)
    time.sleep(0.1)
    ReleaseKey(k)
    time.sleep(0.4)


def hold(k, t):
    PressKey(k)
    time.sleep(t)
    ReleaseKey(k)
    time.sleep(0.5)


def key_down(k):
    PressKey(k)
    time.sleep(0.1)


def key_up(k):
    ReleaseKey(k)
    time.sleep(0.1)


def wtpress(k):
    PressKey(k)
    time.sleep(0.1)
    ReleaseKey(k)
    time.sleep(1.4)
