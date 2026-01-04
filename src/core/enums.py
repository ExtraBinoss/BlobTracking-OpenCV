from enum import Enum

class DetectionMode(str, Enum):
    GRAYSCALE = "Grayscale"
    EDGES = "Edges"
    COLOR = "Color"

class VisualStyle(str, Enum):
    SQUARE = "Square"
    CIRCLE = "Circle"

class Platform(str, Enum):
    WINDOWS = "nt"
    LINUX = "posix"
    MACOS = "darwin" 

class ColorMode(str, Enum):
    SOLID = "Solid"
    EFFECT = "Effect"
    CUSTOM = "Custom"

class ColorEffectType(str, Enum):
    RAINBOW = "Rainbow"
    CYCLE = "Cycle"
    BREATHE = "Breathe"
    RIPPLE = "Ripple"
    FIREWORK = "Firework"
    NONE = "None"

class TextMode(str, Enum):
    NONE = "None"
    INDEX = "Index"
    RANDOM_WORD = "Random Word"
    CUSTOM = "Custom"

class TextPosition(str, Enum):
    RIGHT = "Right"
    TOP = "Top"
    CENTER = "Center"
    BOTTOM = "Bottom"
