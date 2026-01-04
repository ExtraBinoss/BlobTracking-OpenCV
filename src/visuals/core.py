import cv2
import numpy as np
from collections import deque
from .strategies import (
    WhiteColorStrategy, RainbowColorStrategy, CycleColorStrategy,
    TrackedShapeStrategy, FixedShapeStrategy,
    NoTextStrategy, IndexTextStrategy, RandomWordStrategy
)

class VisualStateManager:
    def __init__(self, max_trace_length=20):
        self.traces = {}  # id -> deque of points
        self.max_trace_length = max_trace_length

    def update(self, objects):
        # objects is a dict: id -> (x, y)
        current_ids = set(objects.keys())
        
        # Remove old traces
        for obj_id in list(self.traces.keys()):
            if obj_id not in current_ids:
                del self.traces[obj_id]

        # Update existing and new
        for obj_id, centroid in objects.items():
            if obj_id not in self.traces:
                self.traces[obj_id] = deque(maxlen=self.max_trace_length)
            self.traces[obj_id].appendleft(centroid)

class Visualizer:
    def __init__(self, state_manager):
        self.state = state_manager
        
        # Default Strategies
        self.color_strategy = WhiteColorStrategy()
        self.shape_strategy = FixedShapeStrategy()
        self.text_strategy = IndexTextStrategy()
        
        # Settings
        self.show_center_dot = False
        self.fill_shape = False # Default hollow
        self.fixed_size = 50 
        self.glow_enabled = True
        
        # New Visual Settings
        self.show_traces = True
        self.border_thickness = 2
        self.text_position = "Right" # Options: Right, Top, Center, Bottom
        self.text_size = 14
        self.text_color = (255, 255, 255)
        
        # Tracer Settings
        self.trace_thickness = 2
        self.trace_lifetime = 20  # Number of frames
        self.trace_color = None  # None = use shape color
        
        # Limits
        self.max_blobs = 50

    def set_color_strategy(self, strategy):
        self.color_strategy = strategy

    def set_shape_strategy(self, strategy):
        self.shape_strategy = strategy

    def set_text_strategy(self, strategy):
        self.text_strategy = strategy

    def draw(self, frame, objects, shape_type="square", frame_idx=0): # shape_type kept for legacy signal compatibility for now, but strategy overrides
        # simple objects for trace tracking
        simple_objects = {oid: (o[0], o[1]) for oid, o in objects.items()}
        self.state.update(simple_objects)
        
        overlay = frame.copy()
        
        # Limit to max_blobs
        drawn_count = 0
        for obj_id, data in objects.items():
            if drawn_count >= self.max_blobs:
                break
            drawn_count += 1
            x, y, radius = data # Centroid and radius from tracker
            
            # 1. Geometry
            # We construct a mock rect from the radius for the strategy
            # or pass the centroid. 
            # Strategy expects rect (x,y,w,h) usually.
            mock_rect = (x - radius, y - radius, radius*2, radius*2)
            gx, gy, gw, gh = self.shape_strategy.get_geometry(mock_rect, self.fixed_size)
            
            # 2. Color
            color = self.color_strategy.get_color(obj_id, frame_idx)
            
            # 3. Text
            text = self.text_strategy.get_text(obj_id, frame_idx)

            # Draw Trace
            if self.show_traces:
                trace = self.state.traces.get(obj_id, [])
                if len(trace) > 1:
                    limit = min(len(trace), self.trace_lifetime)
                    trace_col = self.trace_color if self.trace_color else color
                    for i in range(1, limit):
                        # Fade thickness based on age
                        age_factor = 1 - (i / limit)
                        thickness = max(1, int(self.trace_thickness * age_factor * 1.5))
                        cv2.line(frame, trace[i - 1], trace[i], trace_col, thickness)

            # Draw Shape
            # We use gw/gh to determine radius if circle
            draw_radius = gw // 2
            
            center = (gx + draw_radius, gy + draw_radius)
            
            # If "square" was passed from UI, we might want to respect that preference 
            # combined with our strategy? 
            # For now let's assume if it's "circle" we draw circle, else square.
            # But "shape_type" comes from the enum...
            
            is_circle = (shape_type.lower() == "circle")
            
            # Determine thickness: -1 for fill, border_thickness for hollow
            thickness = -1 if self.fill_shape else self.border_thickness
            
            if is_circle:
                cv2.circle(frame, center, draw_radius, color, thickness)
                if self.glow_enabled:
                     # If hollow, glow should also be hollow (thicker border)
                     # If filled, glow is filled
                     glow_thick = -1 if self.fill_shape else (self.border_thickness + 4)
                     cv2.circle(overlay, center, draw_radius + 5, color, glow_thick)
            else:
                top_left = (gx, gy)
                bottom_right = (gx + gw, gy + gh)
                cv2.rectangle(frame, top_left, bottom_right, color, thickness)
                if self.glow_enabled:
                    glow_thick = -1 if self.fill_shape else (self.border_thickness + 4)
                    # Adjust rect for glow size
                    cv2.rectangle(overlay, (gx - 2, gy - 2), (gx + gw + 2, gy + gh + 2), color, glow_thick)
            
            # Draw Center Dot
            if self.show_center_dot:
                cv2.circle(frame, center, 2, (0, 0, 255), -1)

            # Draw Text
            if text:
                # Calculate font scale from text_size (approx conversion)
                font_scale = self.text_size / 24.0  # 24 is baseline
                thickness = max(1, int(self.text_size / 12))
                
                # Calculate position based on self.text_position
                tx, ty = gx + gw + 5, gy + 10 # Default 'Right'
                
                tp = self.text_position.lower()
                if tp == "top":
                    tx = gx
                    ty = gy - 10
                elif tp == "bottom":
                    tx = gx
                    ty = gy + gh + 20
                elif tp == "center":
                    # Rough centering
                    text_dims, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                    tx = center[0] - text_dims[0] // 2
                    ty = center[1] + text_dims[1] // 2
                
                # BGR color (cv2 uses BGR)
                text_color_bgr = (self.text_color[2], self.text_color[1], self.text_color[0])
                cv2.putText(frame, text, (tx, ty), 
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color_bgr, thickness)

        # Apply overlay
        if self.glow_enabled:
            alpha = 0.3
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
