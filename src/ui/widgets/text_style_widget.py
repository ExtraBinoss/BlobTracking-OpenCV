from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QPushButton, QColorDialog, QStackedWidget,
                             QFormLayout, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.ui.widgets.custom_combo import ClickableComboBox

class TextStyleWidget(QWidget):
    """Modular widget for text style configuration."""
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.text_color = QColor(255, 255, 255)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Text Mode Selection
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Text Mode:"))
        self.mode_combo = ClickableComboBox()
        self.mode_combo.addItems(["None", "Index", "Random Word", "Custom"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_row.addWidget(self.mode_combo, 1)
        layout.addLayout(mode_row)
        
        # Sub-properties container (hidden when "None")
        self.sub_props = QWidget()
        sub_lay = QVBoxLayout(self.sub_props)
        sub_lay.setContentsMargins(0, 5, 0, 0)
        sub_lay.setSpacing(8)
        
        # Position
        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("Position:"))
        self.pos_combo = ClickableComboBox()
        self.pos_combo.addItems(["Right", "Top", "Bottom", "Center"])
        self.pos_combo.currentTextChanged.connect(self.emit_settings)
        pos_row.addWidget(self.pos_combo, 1)
        sub_lay.addLayout(pos_row)
        
        # Font Size
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(8, 48)
        self.size_slider.setValue(14)
        self.size_slider.valueChanged.connect(self.emit_settings)
        size_row.addWidget(self.size_slider, 1)
        self.size_label = QLabel("14")
        self.size_slider.valueChanged.connect(lambda v: self.size_label.setText(str(v)))
        size_row.addWidget(self.size_label)
        sub_lay.addLayout(size_row)
        
        # Text Color
        self.color_btn = QPushButton("Text Color")
        self.color_btn.clicked.connect(self.pick_color)
        self.color_btn.setStyleSheet("background-color: #ffffff; color: #000;")
        sub_lay.addWidget(self.color_btn)
        
        layout.addWidget(self.sub_props)
        
        # Default state
        self.sub_props.setVisible(False)  # Hidden when "None"
    
    def on_mode_changed(self, mode):
        self.sub_props.setVisible(mode != "None")
        self.emit_settings()
    
    def pick_color(self):
        color = QColorDialog.getColor(self.text_color)
        if color.isValid():
            self.text_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; color: {'#000' if color.lightness() > 128 else '#fff'};")
            self.emit_settings()
    
    def get_settings(self):
        mode = self.mode_combo.currentText()
        return {
            "text_mode": mode,
            "text_position": self.pos_combo.currentText(),
            "text_size": self.size_slider.value(),
            "text_color": self.text_color.getRgb()[:3]
        }
    
    def emit_settings(self, *args):
        self.settings_changed.emit(self.get_settings())
