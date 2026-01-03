import cv2
import numpy as np
from collections import deque
import random
from .utils import RandomTextGenerator

class VisualStateManager:
    def __init__(self, max_trace_length=20):
        self.traces = {}  # id -> deque of points
        self.texts = {}   # id -> assigned text
        self.colors = {}  # id -> (r, g, b)
        self.max_trace_length = max_trace_length
        self.text_gen = RandomTextGenerator()

    def update(self, objects):
        # objects is a dict: id -> (x, y)
        current_ids = set(objects.keys())
        
        # Remove old traces
        for obj_id in list(self.traces.keys()):
            if obj_id not in current_ids:
                # Optionally keep traces fading out, but for now remove
                del self.traces[obj_id]
                del self.texts[obj_id]
                del self.colors[obj_id]

        # Update existing and new
        for obj_id, centroid in objects.items():
            if obj_id not in self.traces:
                self.traces[obj_id] = deque(maxlen=self.max_trace_length)
                self.texts[obj_id] = self.text_gen.get_random_text()
                # Random neon-ish color
                self.colors[obj_id] = (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )
            
            self.traces[obj_id].appendleft(centroid)

class Visualizer:
    def __init__(self, state_manager):
        self.state = state_manager

    def draw(self, frame, objects, shape="square"):
        # Update state first
        # objects now contains (x, y, radius)
        # We need to pass just {id: (x, y)} to state manager for trace tracking
        # or update state manager to handle the tuple. 
        # Making a cleaner dict for state manager:
        simple_objects = {oid: (o[0], o[1]) for oid, o in objects.items()}
        self.state.update(simple_objects)
        
        overlay = frame.copy()
        
        for obj_id, data in objects.items():
            # Unpack data
            x, y, radius = data
            
            color = self.state.colors.get(obj_id, (0, 255, 0)) # Default green if missing
            text = self.state.texts.get(obj_id, "???")
            trace = self.state.traces.get(obj_id, [])

            # Draw Tracer
            if len(trace) > 1:
                # Limit tracer length visually if it's too long
                limit = min(len(trace), 20)
                for i in range(1, limit):
                    thickness = int(np.sqrt(64 / float(i + 1)) * 2)
                    cv2.line(frame, trace[i - 1], trace[i], color, thickness)

            # Draw Shape
            if shape == "circle":
                cv2.circle(frame, (x, y), radius, color, 2)
                # Outer glow effect (simple)
                cv2.circle(overlay, (x, y), radius + 5, color, -1)
            else:
                # Square
                top_left = (x - radius, y - radius)
                bottom_right = (x + radius, y + radius)
                cv2.rectangle(frame, top_left, bottom_right, color, 2)
                cv2.rectangle(overlay, (x - radius - 2, y - radius - 2), (x + radius + 2, y + radius + 2), color, -1)

            # Draw Text
            cv2.putText(frame, text, (x + radius + 10, y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw ID
            cv2.putText(frame, f"ID: {obj_id}", (x - radius, y - radius - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Apply overlay with transparency for "glow"
        alpha = 0.3
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
