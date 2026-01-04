from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.ui.widgets.custom_combo import ClickableComboBox
from src.ui.widgets.color_picker_widget import CompactColorButton
from src.core.enums import ColorMode, ColorEffectType
from src.ui.utils.tooltip_manager import InfoTooltip

class ColorEffectWidget(QWidget):
    """Modular widget for color/effect configuration."""
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def add_tooltip(self, layout, label_widget, category, key):
        """Helper to append tooltip."""
        tt = InfoTooltip(category, key)
        layout.addWidget(tt)
        layout.addStretch()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Mode Selection
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Color Mode:"))
        self.mode_combo = ClickableComboBox()
        self.mode_combo.addItems([e.value for e in ColorMode])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_row.addWidget(self.mode_combo, 1)
        self.add_tooltip(mode_row, None, "color", "mode")
        layout.addLayout(mode_row)
        
        # Stacked Widget for mode-specific settings
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # --- Page 0: Solid ---
        self.solid_page = QWidget()
        solid_lay = QVBoxLayout(self.solid_page)
        solid_lay.setContentsMargins(0, 5, 0, 0)
        
        self.solid_color_btn = CompactColorButton(QColor(255, 255, 255))
        self.solid_color_btn.colorChanged.connect(self.emit_settings)
        # Create a layout to hold btn + tooltip
        sb_row = QHBoxLayout()
        sb_row.addWidget(self.solid_color_btn)
        self.add_tooltip(sb_row, None, "color", "solid_color")
        solid_lay.addLayout(sb_row)
        self.stack.addWidget(self.solid_page)
        
        # --- Page 1: Effect (Presets) ---
        self.effect_page = QWidget()
        effect_lay = QVBoxLayout(self.effect_page)
        effect_lay.setContentsMargins(0, 5, 0, 0)
        
        self.effect_combo = ClickableComboBox()
        # Drop NONE for preset effects page if desired, or keep all except NONE
        effects = [e.value for e in ColorEffectType if e != ColorEffectType.NONE]
        self.effect_combo.addItems(effects)
        self.effect_combo.currentTextChanged.connect(self.emit_settings)
        # Row for combo + tooltip
        ec_row = QHBoxLayout()
        ec_row.addWidget(self.effect_combo)
        self.add_tooltip(ec_row, None, "color", "effect_type")
        effect_lay.addLayout(ec_row)
        
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
        self.add_tooltip(speed_row, None, "color", "speed")
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
        self.custom_effect_combo.addItems([e.value for e in ColorEffectType])
        self.custom_effect_combo.currentTextChanged.connect(self.emit_settings)
        base_row.addWidget(self.custom_effect_combo, 1)
        self.add_tooltip(base_row, None, "color", "effect_type")
        custom_lay.addLayout(base_row)
        
        # Speed
        cspeed_row = QHBoxLayout()
        cspeed_row.addWidget(QLabel("Speed:"))
        self.custom_speed = QSlider(Qt.Orientation.Horizontal)
        self.custom_speed.setRange(1, 100)
        self.custom_speed.setValue(50)
        self.custom_speed.valueChanged.connect(self.emit_settings)
        cspeed_row.addWidget(self.custom_speed, 1)
        self.add_tooltip(cspeed_row, None, "color", "speed")
        custom_lay.addLayout(cspeed_row)
        
        # Intensity
        intensity_row = QHBoxLayout()
        intensity_row.addWidget(QLabel("Intensity:"))
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(1, 100)
        self.intensity_slider.setValue(75)
        self.intensity_slider.valueChanged.connect(self.emit_settings)
        intensity_row.addWidget(self.intensity_slider, 1)
        self.add_tooltip(intensity_row, None, "color", "intensity")
        custom_lay.addLayout(intensity_row)
        
        # Primary Color
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Primary:"))
        self.custom_color_btn = CompactColorButton(QColor(67, 160, 71))
        self.custom_color_btn.colorChanged.connect(self.emit_settings)
        color_row.addWidget(self.custom_color_btn, 1)
        self.add_tooltip(color_row, None, "color", "primary_color")
        custom_lay.addLayout(color_row)
        
        self.stack.addWidget(self.custom_page)
        
        # Default to Solid
        self.stack.setCurrentIndex(0)
    
    def on_mode_changed(self, mode):
        if mode == ColorMode.SOLID.value:
            self.stack.setCurrentIndex(0)
        elif mode == ColorMode.EFFECT.value:
            self.stack.setCurrentIndex(1)
        else:  # Custom
            self.stack.setCurrentIndex(2)
        self.emit_settings()
    
    def get_settings(self):
        mode = self.mode_combo.currentText()
        settings = {"color_mode": mode}
        
        if mode == ColorMode.SOLID.value:
            settings["solid_color"] = self.solid_color_btn.getRGB()
        elif mode == ColorMode.EFFECT.value:
            settings["effect_name"] = self.effect_combo.currentText()
            settings["effect_speed"] = self.speed_slider.value()
        else:  # Custom
            settings["effect_name"] = self.custom_effect_combo.currentText()
            settings["effect_speed"] = self.custom_speed.value()
            settings["effect_intensity"] = self.intensity_slider.value()
            settings["primary_color"] = self.custom_color_btn.getRGB()
        
        return settings
    
    def emit_settings(self, *args):
        self.settings_changed.emit(self.get_settings())
