import cv2
import numpy as np
from ultralytics import YOLOWorld

class TrafficTracker:
    def __init__(self, model_path='yolov8s-worldv2.pt', num_cameras=4):
        print(f"Loading YOLO-World Zero-Shot Model ({model_path})...")
        # Load the zero-shot model
        self.model = YOLOWorld(model_path)
        
        # Define our restricted custom vocabulary (force large vehicles into ambulance!)
        self.target_class_names = ["car", "motorcycle", "emergency ambulance vehicle"]
        self.model.set_classes(self.target_class_names)
        
        # Quick reference to ID
        self.ambulance_cls_id = self.target_class_names.index("emergency ambulance vehicle")
        self.last_results = [None] * num_cameras
        self.inference_lock = __import__('threading').Lock()
        
    def process_image(self, image, roi_polygon, cam_id=0, run_inference=True):
        """
        Runs YOLO-World detection on a single image.
        Returns the annotated image, the vehicle count, and a boolean if an ambulance is seen.
        """
        if run_inference or self.last_results[cam_id] is None:
            # Added higher conf and iou in predict, and agnostic_nms to prevent multiple detections of same vehicle
            with self.inference_lock:
                self.last_results[cam_id] = self.model.predict(image, verbose=False, conf=0.3, iou=0.4, agnostic_nms=True)
            
        results = self.last_results[cam_id]
        
        annotated_image = image.copy()
        vehicle_count = 0
        is_ambulance_present = False

        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                # get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cls = int(box.cls.cpu().numpy()[0])
                conf = box.conf.cpu().numpy()[0]
                
                # Check for ambulance using the Zero-Shot class
                if cls == self.ambulance_cls_id and conf > 0.15:
                    is_ambulance_present = True
                    color = (0, 0, 255) # Red highlight for ambulance
                else:
                    # Normal vehicle inside ROI check
                    cx = int((x1 + x2) // 2)
                    cy = int(y2)
                    inside = cv2.pointPolygonTest(roi_polygon, (cx, cy), False) >= 0
                    
                    if inside:
                        vehicle_count += 1
                        color = (0, 255, 0) # Green for counted cars
                    else:
                        color = (0, 165, 255) # Orange for cars outside ROI
                    
                # Draw Box
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 4 if is_ambulance_present and cls == self.ambulance_cls_id else 2)
                
                # Draw Label
                label = self.target_class_names[cls].upper()
                if is_ambulance_present and cls == self.ambulance_cls_id:
                    label = "🚨 AMBULANCE DETECTED"
                    
                cv2.putText(annotated_image, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
        # Draw ROI polygon
        cv2.polylines(annotated_image, [roi_polygon], isClosed=True, color=(255, 255, 0), thickness=2)
        cv2.putText(annotated_image, f"Vehicles in ROI: {vehicle_count}", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    
        return annotated_image, vehicle_count, is_ambulance_present
