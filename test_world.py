import cv2
from ultralytics import YOLOWorld

try:
    print("Loading YOLO-World...")
    model = YOLOWorld('yolov8s-worldv2.pt')
    model.set_classes(["car", "truck", "bus", "motorcycle", "ambulance"])
    img = iter(model.predict("https://ultralytics.com/images/bus.jpg", verbose=False)).__next__()
    print("SUCCESS: Classes found =", model.names)
except Exception as e:
    print("FAILED:", e)
