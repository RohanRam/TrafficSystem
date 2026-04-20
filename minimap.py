import cv2
import numpy as np

def draw_minimap(counts, active_lane, timer):
    """
    Draws a highly detailed top-down mini-map of a 4-way intersection.
    """
    size = 600
    img = np.full((size, size, 3), (34, 139, 34), dtype=np.uint8) # Dark Green Grass
    
    # Road properties
    road_width = 140
    c1 = (size // 2) - (road_width // 2)
    c2 = (size // 2) + (road_width // 2)
    mid = size // 2
    
    # Draw Roads
    cv2.rectangle(img, (c1, 0), (c2, size), (90, 90, 90), -1) # Vertical road
    cv2.rectangle(img, (0, c1), (size, c2), (90, 90, 90), -1) # Horizontal road
    cv2.rectangle(img, (c1, c1), (c2, c2), (80, 80, 80), -1) # Intersection Box
    
    # Draw Lane Dividers (Yellow dashed lines)
    for y in range(0, size, 30):
        if not (c1 < y < c2): # Don't draw in the middle of intersection
            cv2.line(img, (mid, y), (mid, y+15), (0, 215, 255), 3)
    for x in range(0, size, 30):
        if not (c1 < x < c2):
            cv2.line(img, (x, mid), (x+15, mid), (0, 215, 255), 3)
            
    # Add clear text labels with flow directions
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Background boxes for text so it's readable over grass
    def draw_label(text, pos):
        (w, h), _ = cv2.getTextSize(text, font, 0.7, 2)
        cv2.rectangle(img, (pos[0]-5, pos[1]-h-5), (pos[0]+w+5, pos[1]+5), (0,0,0), -1)
        cv2.putText(img, text, pos, font, 0.7, (255, 255, 255), 2)

    draw_label("Lane 1 (North) | Flow: DOWN v", (c1 - 320, 40) if c1-320 > 0 else (20, 40))
    draw_label("< Flow: LEFT | Lane 2 (East)", (size - 320, c1 - 40))
    draw_label("^ Flow: UP | Lane 3 (South)", (c2 + 20, size - 20))
    draw_label("Lane 4 (West) | Flow: RIGHT >", (20, c2 + 40))
    
    # Cars logic
    spacing = 50
    
    def draw_cars(count, start_x, start_y, dx, dy, is_horizontal):
        # Swap width/height based on car orientation
        cw, ch = (40, 26) if is_horizontal else (26, 40)
        
        # Max out visually at 5 cars so it doesn't run off screen
        visual_count = min(count, 5)
        for i in range(visual_count): 
            x = start_x + (dx * i)
            y = start_y + (dy * i)
            
            # Car body
            cv2.rectangle(img, (x - cw//2, y - ch//2), (x + cw//2, y + ch//2), (200, 100, 100), -1)
            cv2.rectangle(img, (x - cw//2, y - ch//2), (x + cw//2, y + ch//2), (0, 0, 0), 2)
            
            # Windshield hint to show direction
            if not is_horizontal:
                if dy < 0: # Facing Down
                    cv2.rectangle(img, (x - cw//2 + 4, y + ch//2 - 8), (x + cw//2 - 4, y + ch//2 - 4), (50, 50, 50), -1)
                else: # Facing Up
                    cv2.rectangle(img, (x - cw//2 + 4, y - ch//2 + 4), (x + cw//2 - 4, y - ch//2 + 8), (50, 50, 50), -1)
            else:
                if dx < 0: # Facing Right
                    cv2.rectangle(img, (x + cw//2 - 8, y - ch//2 + 4), (x + cw//2 - 4, y + ch//2 - 4), (50, 50, 50), -1)
                else: # Facing Left
                    cv2.rectangle(img, (x - cw//2 + 4, y - ch//2 + 4), (x - cw//2 + 8, y + ch//2 - 4), (50, 50, 50), -1)

    # Place cars in incoming lanes (Right-Hand Drive system assumption)
    # L1: North heading South (West half of road)
    draw_cars(counts[0], mid - 35, c1 - 40, 0, -spacing, is_horizontal=False)
    # L2: East heading West (North half of road)
    draw_cars(counts[1], c2 + 40, mid - 35, spacing, 0, is_horizontal=True)
    # L3: South heading North (East half of road)
    draw_cars(counts[2], mid + 35, c2 + 40, 0, spacing, is_horizontal=False)
    # L4: West heading East (South half of road)
    draw_cars(counts[3], c1 - 40, mid + 35, -spacing, 0, is_horizontal=True)
    
    # Traffic Lights logic
    def draw_traffic_light(lane_id, px, py, is_horizontal):
        # Draw physical light box
        lw, lh = (16, 36) if not is_horizontal else (36, 16)
        cv2.rectangle(img, (px - lw, py - lh), (px + lw, py + lh), (30, 30, 30), -1)
        cv2.rectangle(img, (px - lw, py - lh), (px + lw, py + lh), (0, 0, 0), 2)
        
        is_green = (active_lane == lane_id)
        
        if not is_horizontal:
            # Red top, Green bottom
            cv2.circle(img, (px, py - 12), 10, (0, 0, 255) if not is_green else (50, 50, 50), -1)
            cv2.circle(img, (px, py + 12), 10, (0, 255, 0) if is_green else (50, 50, 50), -1)
        else:
            # Red left, Green right
            cv2.circle(img, (px - 12, py), 10, (0, 0, 255) if not is_green else (50, 50, 50), -1)
            cv2.circle(img, (px + 12, py), 10, (0, 255, 0) if is_green else (50, 50, 50), -1)
            
    # Place traffic lights at the stop lines of the incoming lanes
    draw_traffic_light(1, c1 - 40, c1 - 40, is_horizontal=False) # L1 light (North)
    draw_traffic_light(2, c2 + 40, c1 - 40, is_horizontal=True)  # L2 light (East)
    draw_traffic_light(3, c2 + 40, c2 + 40, is_horizontal=False) # L3 light (South)
    draw_traffic_light(4, c1 - 40, c2 + 40, is_horizontal=True)  # L4 light (West)
    
    # Draw Central Timer display
    cv2.rectangle(img, (mid - 50, mid - 30), (mid + 50, mid + 30), (0, 0, 0), -1)
    cv2.rectangle(img, (mid - 50, mid - 30), (mid + 50, mid + 30), (255, 255, 255), 2)
    
    text = f"{int(timer)}s"
    # Center text
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
    cv2.putText(img, text, (mid - tw//2, mid + th//2), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
    
    return img
