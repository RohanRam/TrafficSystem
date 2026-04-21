from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import threading
import time
import os
from tracker import TrafficTracker
from signal_controller import SignalController

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tracker = TrafficTracker()
signal_ctrl = SignalController()

global_state = {
    "counts": [0, 0, 0, 0],
    "emergencies": [False, False, False, False],
    "active_lane": 1,
    "timer": 0.0,
    "message": "Initializing live video streams..."
}

# Thread-safe buffer for the latest encoded JPEG frame for each camera
video_frames = [None, None, None, None]

# YOLO PyTorch Inference Lock to prevent multi-threading deadlocks
inference_lock = threading.Lock()

def get_full_roi(shape):
    h, w = shape[:2]
    return np.array([[0,0], [w,0], [w,h], [0,h]], np.int32)

def camera_worker(cam_id, video_path):
    print(f"Starting Live Video Thread for {video_path}")
    
    # Render an instant Loading Frame so the React browser stream doesn't time out waiting for AI to boot
    loading_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(loading_frame, f"AI Booting for {video_path}...", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    _, buffer = cv2.imencode('.jpg', loading_frame)
    video_frames[cam_id] = buffer.tobytes()

    cap = cv2.VideoCapture(video_path)
    
    # If the video fails to open (file not found), fallback to a red error frame
    if not cap.isOpened():
        print(f"WARNING: Could not open {video_path}! Displaying red error frame.")
        err_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(err_frame, f"Video ERROR: {video_path} Missing", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        _, buffer = cv2.imencode('.jpg', err_frame)
        video_frames[cam_id] = buffer.tobytes()
        return

    frame_skip = 3 # Boosted: Process AI every 3rd frame, but stream UI smoothly at 30fps
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            # Video ended, release and explicitly re-open to prevent OpenCV buffer corruption
            cap.release()
            cap = cv2.VideoCapture(video_path)
            continue
            
        frame_count += 1
        roi = get_full_roi(frame.shape)
        
        run_ai = (frame_count % frame_skip == 0)
        
        # Tracker handles YOLO Thread-Safe locking internally now
        ann_img, count, is_em = tracker.process_image(frame, roi, cam_id=cam_id, run_inference=run_ai)
            
        # ALWAYS update Real-time state updates to our backend
        global_state["counts"][cam_id] = count
        global_state["emergencies"][cam_id] = is_em
            
        # ALWAYS Encode frame to JPEG so the MJPEG server streams a butter-smooth video
        ret, buffer = cv2.imencode('.jpg', ann_img)
        if ret:
            video_frames[cam_id] = buffer.tobytes()
                
        # 0.033 gives us approx 30 FPS video playback 
        time.sleep(0.033)

def logic_loop():
    while True:
        # NO MORE MANUAL COUNT DRAINING!
        # Because we have actual looping video, the AI seamlessly handles traffic fluctuations natively!
        
        new_lane, msg = signal_ctrl.update(1.0, global_state["counts"], global_state["emergencies"])
        global_state["active_lane"] = new_lane
        global_state["timer"] = signal_ctrl.timer
        global_state["message"] = msg
        
        time.sleep(1.0)
        
@app.on_event("startup")
def startup_event():
    video_paths = ["cam1.mp4", "cam2.mp4", "cam3.mp4", "cam4.mp4"]
    for i in range(4):
        threading.Thread(target=camera_worker, args=(i, video_paths[i]), daemon=True).start()
        
    threading.Thread(target=logic_loop, daemon=True).start()

@app.get("/api/state")
def get_state():
    return global_state
    
import asyncio

# Lightning-fast MJPEG API Endpoint
async def frame_generator(cam_id):
    while True:
        frame_bytes = video_frames[cam_id]
        if frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Async sleep prevents FastAPI threadpool exhaustion when the user refreshes React
        # Lowered to 0.03 to allow smooth 30FPS streaming
        await asyncio.sleep(0.03)

@app.get("/api/video_feed/{cam_id}")
async def video_feed(cam_id: int):
    # Target React requests from 1 to 4 -> backend index 0 to 3
    idx = cam_id - 1
    if idx < 0 or idx > 3:
        return {"error": "Invalid camera ID"}
    return StreamingResponse(frame_generator(idx), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
