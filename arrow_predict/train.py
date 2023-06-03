from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO('yolov8m.pt')  # load a pretrained model (recommended for training)
    model.to('cuda:0')  # optionally change device
    # Train the model
    model.train(data='arrow/train.yaml', epochs=10, imgsz=434)
    model.export() 
