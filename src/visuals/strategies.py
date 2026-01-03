from abc import ABC, abstractmethod
import random
import colorsys

class ColorStrategy(ABC):
    @abstractmethod
    def get_color(self, object_id, frame_idx):
        pass

class WhiteColorStrategy(ColorStrategy):
    def get_color(self, object_id, frame_idx):
        return (255, 255, 255)

class RainbowColorStrategy(ColorStrategy):
    def get_color(self, object_id, frame_idx):
        # Use object_id to determine hue (stable color per object)
        # Golden ratio conjugate to spread colors
        hue = (object_id * 0.618033988749895) % 1
        rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        return tuple(int(c * 255) for c in rgb)

class CycleColorStrategy(ColorStrategy):
    def get_color(self, object_id, frame_idx):
        # Cycle through colors over time
        hue = (frame_idx * 0.01) % 1
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return tuple(int(c * 255) for c in rgb)

# --- SHAPE STRATEGIES ---
class ShapeStrategy(ABC):
    @abstractmethod
    def get_geometry(self, rect, fixed_size=None):
        pass

class TrackedShapeStrategy(ShapeStrategy):
    def get_geometry(self, rect, fixed_size=None):
        # Returns (x, y, w, h)
        return rect

class FixedShapeStrategy(ShapeStrategy):
    def get_geometry(self, rect, fixed_size=None):
        x, y, w, h = rect
        cx = x + w // 2
        cy = y + h // 2
        size = fixed_size if fixed_size else 50
        # Center the fixed box
        return (cx - size // 2, cy - size // 2, size, size)

# --- TEXT STRATEGIES ---
class TextStrategy(ABC):
    @abstractmethod
    def get_text(self, object_id, frame_idx):
        pass

class NoTextStrategy(TextStrategy):
    def get_text(self, object_id, frame_idx):
        return None

class IndexTextStrategy(TextStrategy):
    def get_text(self, object_id, frame_idx):
        return f"ID: {object_id}"

class RandomWordStrategy(TextStrategy):
    def __init__(self):
        self.words = ["Blob", "Entity", "Target", "Object", "Ghost", "Spirit", "Echo", "Spark"]
        self.assignments = {}
    
    def get_text(self, object_id, frame_idx):
        if object_id not in self.assignments:
            self.assignments[object_id] = random.choice(self.words)
        return self.assignments[object_id]
