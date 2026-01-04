from enum import Enum

class DetectionMode(str, Enum):
    GRAYSCALE = "Grayscale"
    EDGES = "Edges"
    COLOR = "Color"

class VisualStyle(str, Enum):
    SQUARE = "Square"
    CIRCLE = "Circle"
