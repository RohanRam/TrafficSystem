import streamlit as st
import cv2
import numpy as np
import time
import os
from tracker import TrafficTracker
from signal_controller import SignalController
from minimap import draw_minimap

st.set_page_config(layout="wide", page_title="UrbanFlow Dashboard", initial_sidebar_state="collapsed")

# Inject Custom CSS for an Elegant, Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: white;
    }
    
    /* Header Styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 300;
    }
    
    /* Elegant Card specific to Streamlit elements */
    div.stImage > img {
        border-radius: 12px;
        border: 2px solid #334155;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    
    /* Decision Engine Dashboard */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
    }
    
    .green-glow {
        color: #4ade80;
        text-shadow: 0 0 15px rgba(74, 222, 128, 0.5);
        font-size: 2.5rem;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
    }
    .metric-label {
        font-size: 1rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
    }
    div.stButton > button:hover {
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">UrbanFlow Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Intelligent 4-Way Traffic Orchestration System</p>', unsafe_allow_html=True)

# Init models
@st.cache_resource
def load_models():
    tracker = TrafficTracker() # Rely on default yolov8s-worldv2.pt
    return tracker
    
tracker = load_models()
signal_ctrl = SignalController()

start_btn = st.button("Start Analysis")

# Hackathon cheat for Emergency Vehicle demo
simulate_emergency = st.checkbox("🚨 Emergency Override Simulation (Force Demo)", value=False)

if start_btn:
    image_paths = ["cam1.jpg", "cam2.jpg", "cam3.jpg", "cam4.jpg"]
    
    for ip in image_paths:
        if not os.path.exists(ip):
            st.error(f"Missing image file: {ip}!")
            st.stop()
            
    images = [cv2.imread(ip) for ip in image_paths]
    
    def get_full_roi(img):
        height, width = img.shape[:2]
        return np.array([[0, 0], [width, 0], [width, height], [0, height]], np.int32)
            
    roi_polys = [get_full_roi(img) for img in images]
    
    # Process ONCE
    counts = []
    emergencies = []
    annotated_images = []
    
    with st.spinner("Analyzing high-res feeds..."):
        for i in range(4):
            # Using our new YOLO-World Zero-Shot model!
            ann_img, count, is_vis_em = tracker.process_image(images[i], roi_polys[i])
            
            if i == 0 and simulate_emergency:
                is_vis_em = True # Force Lane 1 to have an emergency for demo presentation
                
            annotated_images.append(ann_img)
            counts.append(count)
            emergencies.append(is_vis_em)
            
    # Draw Grid UI
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    cameras_ui = [
        (row1_col1, "Lane 1 (North)"),
        (row1_col2, "Lane 2 (East)"),
        (row2_col1, "Lane 3 (South)"),
        (row2_col2, "Lane 4 (West)")
    ]

    metric_olders = []
    for i, (col, title) in enumerate(cameras_ui):
        with col:
            st.markdown(f"<h3 style='color:#e2e8f0; font-weight:300;'>{title}</h3>", unsafe_allow_html=True)
            st.image(cv2.cvtColor(annotated_images[i], cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
            metric_olders.append(st.empty())

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    eng_col1, eng_col2 = st.columns([1, 1])
    with eng_col1:
        st.markdown("<h3 style='color:#e2e8f0;'>AI Decision Engine</h3>", unsafe_allow_html=True)
        status_placeholder = st.empty()
    with eng_col2:
        st.markdown("<h3 style='color:#e2e8f0;'>Live Minimap</h3>", unsafe_allow_html=True)
        minimap_placeholder = st.empty()

    # Simulation Loop
    while True:
        dt = 1.0
        active_lane, msg = signal_ctrl.update(dt, counts, emergencies)
        
        for i in range(4):
            sig_color = "#4ade80" if active_lane == (i + 1) else "#ef4444"
            sig_text = "🟢 ACTIVE" if active_lane == (i + 1) else "🔴 STOP"
            
            html_metric = f"""
            <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-top:5px; text-align:center;'>
                <span style='color:white; margin-right:20px;'>Density: <b>{counts[i]}</b></span>
                <span style='color:{sig_color}; font-weight:bold;'>{sig_text}</span>
            </div>
            """
            metric_olders[i].markdown(html_metric, unsafe_allow_html=True)
        
        # Engine UI Glass Card
        status_html = f"""
        <div class="glass-card">
            <div class="metric-label">System State</div>
            <h2 class="green-glow">LANE {active_lane} IS GREEN</h2>
            <div style="margin-top:20px;">
                <span class="metric-value">{signal_ctrl.timer:.1f}s</span><br>
                <span class="metric-label">remaining</span>
            </div>
            <p style="color: #fbbf24; margin-top: 15px; font-weight: 300;">{msg}</p>
        </div>
        """
        status_placeholder.markdown(status_html, unsafe_allow_html=True)
        
        minimap_img = draw_minimap(counts, active_lane, signal_ctrl.timer)
        minimap_placeholder.image(cv2.cvtColor(minimap_img, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
        
        time.sleep(1.0)
