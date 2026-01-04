from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QPushButton, QColorDialog, QStackedWidget,
                             QFormLayout, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.ui.widgets.custom_combo import ClickableComboBox

class ColorEffectWidget(QWidget):
    """Modular widget for color/effect configuration."""
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.current_color = QColor(255, 255, 255)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Mode Selection
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Color Mode:"))
        self.mode_combo = ClickableComboBox()
        self.mode_combo.addItems(["Solid", "Effect", "Custom"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_row.addWidget(self.mode_combo, 1)
        layout.addLayout(mode_row)
        
        # Stacked Widget for mode-specific settings
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # --- Page 0: Solid ---
        self.solid_page = QWidget()
        solid_lay = QVBoxLayout(self.solid_page)
        solid_lay.setContentsMargins(0, 5, 0, 0)
        
        self.color_btn = QPushButton("Pick Color")
        self.color_btn.clicked.connect(self.pick_solid_color)
        self.color_btn.setStyleSheet("background-color: #ffffff; color: #000;")
        solid_lay.addWidget(self.color_btn)
        self.stack.addWidget(self.solid_page)
        
        # --- Page 1: Effect (Presets) ---
        self.effect_page = QWidget()
        effect_lay = QVBoxLayout(self.effect_page)
        effect_lay.setContentsMargins(0, 5, 0, 0)
        
        self.effect_combo = ClickableComboBox()
        self.effect_combo.addItems(["Rainbow", "Cycle", "Breathe", "Ripple", "Firework"])
        self.effect_combo.currentTextChanged.connect(self.emit_settings)
        effect_lay.addWidget(self.effect_combo)
        
        # Effect Speed
        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_slider.valueChanged.connect(self.emit_settings)
        speed_row.addWidget(self.speed_slider, 1)
        self.speed_label = QLabel("50")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(str(v)))
        speed_row.addWidget(self.speed_label)
        effect_lay.addLayout(speed_row)
        
        self.stack.addWidget(self.effect_page)
        
        # --- Page 2: Custom ---
        self.custom_page = QWidget()
        custom_lay = QVBoxLayout(self.custom_page)
        custom_lay.setContentsMargins(0, 5, 0, 0)
        
        # Effect Base
        base_row = QHBoxLayout()
        base_row.addWidget(QLabel("Base Effect:"))
        self.custom_effect_combo = ClickableComboBox()
        self.custom_effect_combo.addItems(["None", "Rainbow", "Cycle", "Breathe", "Ripple", "Firework"])
        self.custom_effect_combo.currentTextChanged.connect(self.emit_settings)
        base_row.addWidget(self.custom_effect_combo, 1)
        custom_lay.addLayout(base_row)
        
        # Speed
        cspeed_row = QHBoxLayout()
        cspeed_row.addWidget(QLabel("Speed:"))
        self.custom_speed = QSlider(Qt.Orientation.Horizontal)
        self.custom_speed.setRange(1, 100)
        self.custom_speed.setValue(50)
        self.custom_speed.valueChanged.connect(self.emit_settings)
        cspeed_row.addWidget(self.custom_speed, 1)
        custom_lay.addLayout(cspeed_row)
        
        # Intensity
        intensity_row = QHBoxLayout()
        intensity_row.addWidget(QLabel("Intensity:"))
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(1, 100)
        self.intensity_slider.setValue(75)
        self.intensity_slider.valueChanged.connect(self.emit_settings)
        intensity_row.addWidget(self.intensity_slider, 1)
        custom_lay.addLayout(intensity_row)
        
        # Primary Color
        self.custom_color_btn = QPushButton("Primary Color")
        self.custom_color_btn.clicked.connect(self.pick_custom_color)
        self.custom_color_btn.setStyleSheet("background-color: #43a047; color: #fff;")
        custom_lay.addWidget(self.custom_color_btn)
        
        self.stack.addWidget(self.custom_page)
        
        # Default to Solid
        self.stack.setCurrentIndex(0)
    
    def on_mode_changed(self, mode):
        if mode == "Solid":
            self.stack.setCurrentIndex(0)
        elif mode == "Effect":
            self.stack.setCurrentIndex(1)
        else:  # Custom
            self.stack.setCurrentIndex(2)
        self.emit_settings()
    
    def pick_solid_color(self):
        color = QColorDialog.getColor(self.current_color)
        if color.isValid():
            self.current_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; color: {'#000' if color.lightness() > 128 else '#fff'};")
            self.emit_settings()
    
    def pick_custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.custom_color_btn.setStyleSheet(f"background-color: {color.name()}; color: {'#000' if color.lightness() > 128 else '#fff'};")
            self.emit_settings()
    
    def get_settings(self):
        mode = self.mode_combo.currentText()
        settings = {"color_mode": mode}
        
        if mode == "Solid":
            settings["solid_color"] = self.current_color.getRgb()[:3]
        elif mode == "Effect":
            settings["effect_name"] = self.effect_combo.currentText()
            settings["effect_speed"] = self.speed_slider.value()
        else:  # Custom
            settings["effect_name"] = self.custom_effect_combo.currentText()
            settings["effect_speed"] = self.custom_speed.value()
            settings["effect_intensity"] = self.intensity_slider.value()
            # Parse color from button stylesheet (hack, but works)
            style = self.custom_color_btn.styleSheet()
            if "background-color:" in style:
                hex_color = style.split("background-color:")[1].split(";")[0].strip()
                c = QColor(hex_color)
                settings["primary_color"] = c.getRgb()[:3]
        
        return settings
    
    def emit_settings(self, *args):
        self.settings_changed.emit(self.get_settings())
