class SignalController:
    def __init__(self, min_green_time=5, max_green_time=45):
        self.min_green_time = min_green_time
        self.max_green_time = max_green_time
        
        self.current_green_lane = 1 # 1, 2, 3, or 4
        self.timer = self.min_green_time
        
        self.in_emergency = False
        self.saved_state = None
        
    def update(self, delta_time, counts, emergencies):
        self.timer -= delta_time
        status_msg = "Traffic monitoring active."

        # --- Emergency Overrides ---
        emergency_lane = None
        for i, is_em in enumerate(emergencies):
            if is_em:
                emergency_lane = i + 1
                break
                
        if emergency_lane:
            if not self.in_emergency:
                # Save previous state before overriding
                self.in_emergency = True
                self.saved_state = {
                    'lane': self.current_green_lane,
                    'timer': max(self.timer, 2.0) # Ensure it has at least 2s when returning
                }
                # Grant a full green cycle timer for the ambulance
                self.timer = float(self.max_green_time)
            
            self.current_green_lane = emergency_lane
            if self.timer < 0:
                self.timer = 0
            return emergency_lane, f"🚨 EMERGENCY OVERRIDE - LANE {emergency_lane} FORCE GREEN"
            
        elif self.in_emergency:
            # Emergency just cleared, restore old state!
            self.in_emergency = False
            if self.saved_state:
                self.current_green_lane = self.saved_state['lane']
                self.timer = self.saved_state['timer']
                self.saved_state = None
            status_msg = f"Ambulance passed! Resuming normal operation on Lane {self.current_green_lane}."
            
        # --- Normal Comparative Logic ---
        
        # Determine the next lane in the cycle (1 -> 2 -> 3 -> 4 -> 1)
        next_lane = self.current_green_lane + 1 if self.current_green_lane < 4 else 1
        
        if self.timer <= 0:
            total_waiting = sum(counts)
            
            if total_waiting == 0:
                # All empty, just cycle minimum time
                self.current_green_lane = next_lane
                self.timer = self.min_green_time
                status_msg = f"Roads empty. Cycling to Lane {self.current_green_lane}."
            else:
                # Let's find the best next lane. We can just cycle, or we can skip empty lanes!
                # For this logic: keep cycling, but skip lanes that have 0 cars.
                found_next = False
                for _ in range(4):
                    if counts[next_lane - 1] > 0:
                        self.current_green_lane = next_lane
                        found_next = True
                        break
                    next_lane = next_lane + 1 if next_lane < 4 else 1
                    
                if not found_next:
                    # Fallback
                    self.current_green_lane = next_lane
                    
                target_count = counts[self.current_green_lane - 1]
                
                # Dynamic Time: Base Time + Weight factor.
                weight = target_count / total_waiting
                calculated_time = max(self.min_green_time, int(self.max_green_time * weight * 1.5))
                calculated_time = min(self.max_green_time, calculated_time)
                
                self.timer = calculated_time
                status_msg = f"Traffic compared. Lane {self.current_green_lane} wins {calculated_time}s based on density."
                
        else:
            # Dynamic early switch: If the current lane is currently empty while others are waiting
            current_count = counts[self.current_green_lane - 1]
            waiting_others = sum(counts) - current_count
            
            if current_count == 0 and waiting_others > 0 and self.timer > 3:
                status_msg = f"Lane {self.current_green_lane} is completely idle. Early switch triggered!"
                self.timer = 0 # Force switch on next tick
                
        return self.current_green_lane, status_msg
