from ultralytics import YOLO
import cv2
if __name__ == '__main__':
    # Load a model
    model = YOLO("C:\\Users\\wyn9c\\Documents\\warthunder\\warthunder-cv2\\runs\\detect\\train\\weights\\best.pt")  # load a pretrained model (recommended for training)
    img = "arrow\\data_split\\images\\train\\1685730915180.433.jpg"
    res = model(img)
    res_plotted = res[0].plot()
    cv2.imshow("result", res_plotted)   
cv2.waitKey(0)
