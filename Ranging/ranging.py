#请确保将"path_to_yolo_config_file"和"path_to_yolo_weights_file"替换为你实际的YOLO配置文件和权重文件的路径。同时，
# 将"path_to_image.jpg"替换为你要检测的实际图像文件的路径。


import cv2
import numpy as np

# 加载YOLO模型
net = cv2.dnn.readNetFromDarknet("path_to_yolo_config_file", "path_to_yolo_weights_file")

# 配置其他参数
win_width = 1920
win_height = 1200
mid_width = int(win_width / 2)
mid_height = int(win_height / 2)
foc = 2810.0
real_wid = 11.69
font = cv2.FONT_HERSHEY_SIMPLEX
w_ok = 1

# 加载图像
image_path = "path_to_image.jpg"
image = cv2.imread(image_path)

# 进行目标检测
blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
net.setInput(blob)
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
outputs = net.forward(output_layers)

# 处理检测结果
boxes = []
confidences = []
class_ids = []

for output in outputs:
    for detection in output:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5 and class_id == 0:  # 仅保留人物目标
            center_x = int(detection[0] * win_width)
            center_y = int(detection[1] * win_height)
            width = int(detection[2] * win_width)
            height = int(detection[3] * win_height)
            x = int(center_x - width / 2)
            y = int(center_y - height / 2)
            boxes.append([x, y, width, height])
            confidences.append(float(confidence))
            class_ids.append(class_id)

# 应用非最大抑制以去除重叠的边界框
indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

# 对每个检测到的人物目标进行测距
for i in indices:
    i = i[0]
    x, y, width, height = boxes[i]
    cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)
    w_ok = width

    dis_inch = (real_wid * foc) / (w_ok - 2)
    dis_cm = dis_inch * 2.54

    label = "Distance: {:.2f} cm".format(dis_cm)
    cv2.putText(image, label, (x, y - 10), font, 0.8, (0, 255, 0), 2)

# 显示结果图像
cv2.imshow("Result", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

