import cv2
import numpy as np
from PIL import ImageGrab
import time
sr=(969, 288, 1195, 388)

# Create a NumPy array with some random data
box = (sr)
print(box)

time.sleep(5)


im = ImageGrab.grab(bbox=(box))
im.save('screenshot.png')



im = np.array(im)
im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

lower_green = np.array([0, 100, 0])
upper_green = np.array([100, 255, 100])
mask_green = cv2.inRange(im, lower_green, upper_green)

lower_blue = np.array([0, 0, 100])
upper_blue = np.array([100, 100, 255])
mask_blue = cv2.inRange(im, lower_blue, upper_blue)

if cv2.countNonZero(mask_green) > 0 and cv2.countNonZero(mask_blue) > 0:
    print('蓝色绿色存在')
else:
    print('绿色蓝色不存在')


