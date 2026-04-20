import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [state, setState] = useState(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/state");
        const data = await res.json();
        setState(data);
      } catch (e) {
        console.error("Error fetching state");
      }
    };
    
    fetchState();
    const interval = setInterval(fetchState, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!state) {
    return <div style={{ color: '#0f172a', textAlign: 'center', marginTop: '100px' }}><h1>Loading UrbanFlow Video Engine...</h1><p>Ensure FastAPI is running on port 8000.</p></div>
  }

  const { counts, emergencies, active_lane, timer, message } = state;

  const getSignalStatus = (laneId) => {
    return active_lane === laneId;
  };

  const laneLabels = [
    "Lane 1 (North)",
    "Lane 2 (East)",
    "Lane 3 (South)",
    "Lane 4 (West)"
  ];

  const animateClasses = [
    "drive-north-south",
    "drive-east-west",
    "drive-south-north",
    "drive-west-east"
  ];

  const queueClasses = [
    "arrive-north-south",
    "arrive-east-west",
    "arrive-south-north",
    "arrive-west-east"
  ];

  // Dynamic Vector Mathematics Drawing Engine
  const drawCars = (laneIndex, count, isEm) => {
    const cars = [];
    const isGreen = getSignalStatus(laneIndex + 1);

    for(let i=0; i<count; i++) {
       let style = {};
       const isAmbulance = (isEm && i===0); 
       
       let className = `map-car ${isAmbulance ? 'map-ambulance' : ''}`;
       
       // Continuous Queue Positioning
       const offset = 35 - (i * 8); 

       if (laneIndex === 0) {
           style = { left: '44%', top: `${offset}%`, width: '14px', height: '24px' };
       } else if (laneIndex === 1) {
           style = { top: '44%', right: `${offset}%`, width: '24px', height: '14px' };
       } else if (laneIndex === 2) {
           style = { left: '54%', bottom: `${offset}%`, width: '14px', height: '24px' };
       } else {
           style = { top: '54%', left: `${offset}%`, width: '24px', height: '14px' };
       }

       if (isGreen) {
           className += ` ${animateClasses[laneIndex]}`;
           // Physical Velocity calculation: T = D * (base_time / distance_ratio)
           const distance = 110 - offset;
           const duration = (distance / 100) * 1.8; 
           style.animationDuration = `${Math.max(0.5, duration)}s`;
           style.animationDelay = `${i * 0.28}s`;
       } else {
           className += ` ${queueClasses[laneIndex]}`;
           const distance = offset - (-10);
           const duration = (distance / 100) * 1.0;
           // If they are deep back in the infinite queue off-map, don't run arrive interpolation!
           if (distance > 0) {
               style.animationDuration = `${duration}s`;
           } else {
               style.animationDuration = `0s`;
           }
       }

       cars.push(<div key={`car-${laneIndex}-${i}`} className={className} style={style}></div>);
    }
    return cars;
  }

  return (
    <div className="dashboard">
      <header className="header">
        <h1>UrbanFlow Core</h1>
        <p>Intelligent 4-Way Traffic Orchestration System</p>
      </header>
      
      <div className="grid-container">
        
        {/* Top Split Level */}
        <div className="top-section">
          <div className="cameras-grid">
            {[0, 1, 2, 3].map((i) => {
              const laneId = i + 1;
              const isGreen = getSignalStatus(laneId);
              
              return (
                <div key={i} className="camera-card">
                  <div className="card-header">
                    <span className="card-title">
                      {laneLabels[i]} 
                      <span style={{marginLeft: '12px', color: '#64748b', fontSize: '0.9rem'}}>Vol: {counts[i]}</span>
                      {emergencies[i] && <span className="ambulance-badge">🚨 AMBULANCE</span>}
                    </span>
                    
                    <span className={`signal-badge ${isGreen ? 'signal-green' : 'signal-red'}`}>
                      {isGreen ? '🟩 GREEN' : '🟥 RED'}
                    </span>
                  </div>
                  {/* DIRECT HD MJPEG STREAM TARGETING FASTAPI ENDPOINTS! */}
                  <img src={`http://localhost:8000/api/video_feed/${laneId}`} className="cam-image" alt={`Live Feed ${laneId}`} />
                </div>
              );
            })}
          </div>

          <div className="control-panel">
            <div className="engine-card">
              <div className="metric-label">System State</div>
              <h2 className={active_lane ? "green" : "red"}>
                LANE {active_lane} IS GREEN
              </h2>
              <div className="timer">{timer.toFixed(1)}s</div>
              <div className="metric-label">Remaining</div>
              <div className="status-msg">{message}</div>
            </div>
          </div>
        </div>

        {/* Massive Dynamic Bottom Minimap Level */}
        <div className="bottom-section">
          <div className="minimap-card">
             <div className="metric-label" style={{marginBottom: '10px', textAlign: 'center'}}>Live Interactive Intersection Simulation</div>
             
             {/* Externalized Timer to prevent car overlap in the map center */}
             <div style={{ textAlign: 'center', marginBottom: '10px', background: '#0f172a', color: 'white', borderRadius: '12px', padding: '10px 20px', width: 'fit-content', margin: '0 auto 15px' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 500, marginRight: '15px', color: '#94a3b8' }}>Intersection Engine Timer: </span>
                <span style={{ fontSize: '2.5rem', fontWeight: 700, color: '#10b981' }}>{Math.floor(timer)}s</span>
             </div>

             <div className="minimap-container">
                <div className="road-vert">
                   <div className="lane-divider-vert"></div>
                </div>
                <div className="road-horiz">
                   <div className="lane-divider-horiz"></div>
                </div>
                <div className="intersection">
                   {/* Center is left blank so cars can safely pass without visual overlap! */}
                </div>
                
                {/* Detailed Traffic Light Posts */}
                {[1, 2, 3, 4].map((lane) => {
                   const isGrn = active_lane === lane;
                   return (
                     <div key={`light-${lane}`} className={`traffic-light-post lt${lane}`}>
                        <div className="bulb bulb-red" style={{ opacity: isGrn ? 0.15 : 1 }}></div>
                        <div className="bulb bulb-yellow" style={{ opacity: 0.15 }}></div>
                        <div className="bulb bulb-green" style={{ opacity: isGrn ? 1 : 0.15 }}></div>
                     </div>
                   );
                })}
                
                {/* Simulated Moving Cars Natively */}
                {drawCars(0, counts[0], emergencies[0])}
                {drawCars(1, counts[1], emergencies[1])}
                {drawCars(2, counts[2], emergencies[2])}
                {drawCars(3, counts[3], emergencies[3])}
             </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
