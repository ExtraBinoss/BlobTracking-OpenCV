from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.ui.widgets.custom_combo import ClickableComboBox
from src.ui.widgets.color_picker_widget import CompactColorButton
from src.core.enums import TextMode, TextPosition

class TextStyleWidget(QWidget):
    """Modular widget for text style configuration."""
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Text Mode Selection
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Text Mode:"))
        self.mode_combo = ClickableComboBox()
        self.mode_combo.addItems([e.value for e in TextMode])
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
        self.pos_combo.addItems([e.value for e in TextPosition])
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
        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Color:"))
        self.text_color_btn = CompactColorButton(QColor(255, 255, 255))
        self.text_color_btn.colorChanged.connect(self.emit_settings)
        color_row.addWidget(self.text_color_btn, 1)
        sub_lay.addLayout(color_row)
        
        layout.addWidget(self.sub_props)
        
        # Default state
        self.sub_props.setVisible(False)  # Hidden when "None"
    
    def on_mode_changed(self, mode):
        self.sub_props.setVisible(mode != TextMode.NONE.value)
        self.emit_settings()
    
    def get_settings(self):
        mode = self.mode_combo.currentText()
        return {
            "text_mode": mode,
            "text_position": self.pos_combo.currentText(),
            "text_size": self.size_slider.value(),
            "text_color": self.text_color_btn.getRGB()
        }
    
    def emit_settings(self, *args):
        self.settings_changed.emit(self.get_settings())
