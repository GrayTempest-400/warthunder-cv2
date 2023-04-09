#请注意，您需要将上面的代码中的“tank_classifier.xml”替换为您自己训练的坦克分类器的名称。此外，您还需要将“test_image.jpg”替换为要检测的图像的名称。
import cv2

# Load the cascade
tank_cascade = cv2.CascadeClassifier('tank_classifier.xml')

# Read the input image
img = cv2.imread('input_image.jpg')

# Convert into grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect tanks
tanks = tank_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

# Draw rectangles around the tanks
for (x, y, w, h) in tanks:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

# Display the output
cv2.imshow('img', img)
cv2.waitKey()