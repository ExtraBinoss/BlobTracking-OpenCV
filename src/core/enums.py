from enum import Enum

class DetectionMode(str, Enum):
    GRAYSCALE = "grayscale"
    EDGES = "edges"
    COLOR = "color"

class VisualStyle(str, Enum):
    SQUARE = "square"
    CIRCLE = "circle"
