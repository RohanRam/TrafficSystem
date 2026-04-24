# 🚦 UrbanFlow: Intelligent Traffic Management System

## 📌 Overview
UrbanFlow is an intelligent traffic management system designed to optimize traffic signal timings based on real-time vehicle density and prioritize emergency vehicles like ambulances.

The system uses computer vision and machine learning techniques to analyze traffic conditions and dynamically control signals, reducing congestion and improving response times for emergency services.

---

## 📸 Demo Output

### Traffic Detection
![Traffic Detection](<img src="ss1.png" width="50%"/>)

### Signal Control
![Signal Control](ss2.png)

## 🎯 Problem Statement
Traditional traffic systems operate on fixed timers, which:
- Do not adapt to real-time traffic conditions  
- Cause unnecessary congestion  
- Delay emergency vehicles (ambulances, fire trucks, etc.)  

UrbanFlow aims to solve this by making traffic signals **adaptive and intelligent**.

---

## 💡 Key Features

### 🚗 Vehicle Detection & Counting
- Uses computer vision to detect vehicles from traffic camera feeds  
- Counts vehicles in each lane  
- Helps determine traffic density  

### 🚦 Dynamic Signal Timing
- Adjusts green light duration based on vehicle count  
- Reduces waiting time and improves flow efficiency  

### 🚑 Emergency Vehicle Priority
- Detects ambulances using:
  - Audio detection (siren recognition using ML models like YAMNet)  
  - (Optional) Visual identification  
- Automatically gives priority signal (green light path)

### 🧠 Intelligent Decision System
- Combines:
  - Vehicle density  
  - Lane priority  
  - Emergency signals  
- Makes real-time decisions for signal control  

### 🔮 (Planned) Predictive Traffic Flow
- Use ML to predict traffic patterns  
- Pre-adjust signals before congestion builds  

---

## 🏗️ System Architecture

```
Traffic Cameras (4 Lanes)
        ↓
Image Processing (Vehicle Detection)
        ↓
Vehicle Count per Lane
        ↓
Audio Input (Siren Detection)
        ↓
Decision Engine (ML + Rules)
        ↓
Traffic Signal Control
        ↓
Simulation (SUMO / Prototype)
```

---

## 🛠️ Tech Stack

### 💻 Programming
- Python

### 🧠 Machine Learning
- TensorFlow  
- TensorFlow Hub  
- YAMNet  

### 👁️ Computer Vision
- OpenCV  
- NumPy  

### 🔊 Audio Processing
- Librosa  

### 🚦 Simulation (Planned)
- SUMO (Simulation of Urban Mobility)

---

## ⚙️ Installation

```bash
git clone https://github.com/RohanRam/UrbanFlow.git
cd UrbanFlow

pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python main.py
```

### Input
- Traffic images/videos  
- Audio input (for siren detection)  

### Output
- Vehicle count per lane  
- Signal timing decisions  
- Emergency priority activation  

---

## 🧪 Example Workflow

1. Capture traffic from 4 cameras (junction)  
2. Detect and count vehicles in each lane  
3. Detect ambulance siren using audio model  
4. Decision engine:
   - If ambulance detected → give priority  
   - Else → adjust signal timing based on density  

---

## 📊 Future Enhancements

- 🔮 Traffic prediction using historical data  
- 🌐 Real-time IoT-based camera integration  
- 📱 Mobile dashboard for traffic monitoring  
- 🧭 Route optimization for emergency vehicles  
- 🤖 Deep learning-based vehicle classification  

---

## 🚀 Unique Value Proposition

- Combines **audio + vision intelligence**  
- Handles **Indian traffic conditions (unstructured roads)**  
- Focuses on **real-world emergency prioritization**  
- Scalable towards **smart city infrastructure**

---

## 👨‍💻 Contributors


- Rohan Ram
- [Devnath P](https://github.com/devnathdivya6-hash) 
- [Aadish K](https://github.com/Aadishk) 
- [Addwin Antony Stephen](https://github.com/Addwin2004)

---

## 📜 License
This project is for academic and research purposes.
