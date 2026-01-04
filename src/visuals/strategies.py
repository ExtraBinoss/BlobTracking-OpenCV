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
    def __init__(self, speed=50):
        self.speed = speed
    
    def get_color(self, object_id, frame_idx):
        # Cycle through colors over time
        hue = (frame_idx * (self.speed / 5000)) % 1
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return tuple(int(c * 255) for c in rgb)

class SolidColorStrategy(ColorStrategy):
    def __init__(self, color=(255, 255, 255)):
        # Convert RGB to BGR for OpenCV
        self.color = (color[2], color[1], color[0])
    
    def get_color(self, object_id, frame_idx):
        return self.color

class BreatheColorStrategy(ColorStrategy):
    def __init__(self, base_color=(67, 160, 71), speed=50, intensity=75):
        # Convert RGB to BGR for OpenCV
        self.base_color = (base_color[2], base_color[1], base_color[0])
        self.speed = speed
        self.intensity = intensity
    
    def get_color(self, object_id, frame_idx):
        import math
        # Pulsing brightness
        factor = (math.sin(frame_idx * (self.speed / 500)) + 1) / 2  # 0 to 1
        min_brightness = 1 - (self.intensity / 100)
        brightness = min_brightness + factor * (1 - min_brightness)
        return tuple(int(c * brightness) for c in self.base_color)

class RippleColorStrategy(ColorStrategy):
    def __init__(self, speed=50, intensity=75):
        self.speed = speed
        self.intensity = intensity
    
    def get_color(self, object_id, frame_idx):
        import math
        # Each object gets a phase offset based on ID
        phase = (frame_idx * (self.speed / 500)) + (object_id * 0.5)
        hue = (math.sin(phase) + 1) / 2
        saturation = self.intensity / 100
        rgb = colorsys.hsv_to_rgb(hue, saturation, 1.0)
        return tuple(int(c * 255) for c in rgb)

class FireworkColorStrategy(ColorStrategy):
    def __init__(self, speed=50, intensity=75):
        self.speed = speed
        self.intensity = intensity
        self.sparks = {}
    
    def get_color(self, object_id, frame_idx):
        # Randomly "explode" with bright colors, then fade
        if object_id not in self.sparks or frame_idx - self.sparks[object_id]['start'] > 30:
            # New spark
            hue = random.random()
            self.sparks[object_id] = {'hue': hue, 'start': frame_idx}
        
        spark = self.sparks[object_id]
        age = frame_idx - spark['start']
        brightness = max(0, 1 - (age / 30))  # Fade out over 30 frames
        rgb = colorsys.hsv_to_rgb(spark['hue'], 1.0, brightness)
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
