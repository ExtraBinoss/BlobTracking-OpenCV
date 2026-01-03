from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QSlider, QLabel, QPushButton, QFileDialog, QHBoxLayout,
                             QScrollArea, QCheckBox, QColorDialog, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from src.core.enums import DetectionMode, VisualStyle
from src.ui.widgets.collapsible_box import CollapsibleBox
from src.ui.widgets.custom_combo import ClickableComboBox

class ControlPanel(QWidget):
    params_changed = pyqtSignal(dict)
    file_selected = pyqtSignal(str)
    export_requested = pyqtSignal()
    debug_toggled = pyqtSignal(bool) 
    shape_changed = pyqtSignal(str) # Legacy? Maybe keep for now
    visuals_changed = pyqtSignal(dict) # New signal for modular visuals
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10) 

        # File Selection (Always visible)
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("border: 1px solid #555; padding: 5px; border-radius: 6px;") 
        btn_file = QPushButton("Select Video")
        btn_file.clicked.connect(self.select_file)
        layout.addWidget(btn_file)
        layout.addWidget(self.file_label)
        layout.addWidget(QLabel("<hr>"))

        # Visual Config Box
        self.vis_box = CollapsibleBox("Visual Settings")
        vis_lay = QVBoxLayout()
        
        # Color Mode
        vis_lay.addWidget(QLabel("Color Mode:"))
        self.color_combo = ClickableComboBox()
        self.color_combo.addItems(["White", "Rainbow", "Cycle"])
        self.color_combo.currentTextChanged.connect(self.emit_visuals)
        vis_lay.addWidget(self.color_combo)

        # Text Mode
        vis_lay.addWidget(QLabel("Text Mode:"))
        self.text_combo = ClickableComboBox()
        self.text_combo.addItems(["None", "Index", "Random Word"])
        self.text_combo.currentTextChanged.connect(self.emit_visuals)
        vis_lay.addWidget(self.text_combo)

        # Shape Logic
        vis_lay.addWidget(QLabel("Shape Style:"))
        self.shape_combo = ClickableComboBox()
        self.shape_combo.addItems([e.value for e in VisualStyle])
        self.shape_combo.currentTextChanged.connect(self.emit_visuals) # Use new signal logic
        vis_lay.addWidget(self.shape_combo)
        
        # Fixed Size Toggle & Spinner
        size_row = QHBoxLayout()
        self.fixed_size_chk = QCheckBox("Fixed Size")
        self.fixed_size_chk.toggled.connect(self.emit_visuals)
        size_row.addWidget(self.fixed_size_chk)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 500)
        self.size_spin.setValue(50)
        self.size_spin.setSuffix(" px")
        self.size_spin.valueChanged.connect(self.emit_visuals)
        size_row.addWidget(self.size_spin)
        vis_lay.addLayout(size_row)

        # Toggles
        self.dot_chk = QCheckBox("Show Centroid Dot")
        self.dot_chk.setChecked(True)
        self.dot_chk.toggled.connect(self.emit_visuals)
        vis_lay.addWidget(self.dot_chk)

        self.vis_box.content_layout.addLayout(vis_lay)
        layout.addWidget(self.vis_box)
        
        # Detection Mode Box
        self.detect_box = CollapsibleBox("Detection Settings")
        
        # Mode Selection
        mode_lay = QVBoxLayout()
        mode_lay.addWidget(QLabel("Mode:"))
        self.mode_combo = ClickableComboBox()
        self.mode_combo.addItems([e.value for e in DetectionMode])
        self.mode_combo.setCurrentText(DetectionMode.EDGES.value)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_lay.addWidget(self.mode_combo)
        mode_lay.addWidget(QLabel("<hr>"))
        self.detect_box.content_layout.addLayout(mode_lay)

        # Mode Specific Settings (Added to Detect Box)
        # 1. Grayscale
        self.gray_widget = QWidget()
        gray_lay = QVBoxLayout(self.gray_widget)
        gray_lay.setContentsMargins(0,0,0,0)
        self.thresh_slider = self.create_slider("Threshold", 0, 255, 127, gray_lay)
        self.detect_box.add_widget(self.gray_widget)

        # 2. Edges
        self.edge_widget = QWidget()
        edge_lay = QVBoxLayout(self.edge_widget)
        edge_lay.setContentsMargins(0,0,0,0)
        self.canny_low_slider = self.create_slider("Low Threshold", 0, 255, 50, edge_lay)
        self.canny_high_slider = self.create_slider("High Threshold", 0, 255, 150, edge_lay)
        self.detect_box.add_widget(self.edge_widget)

        # 3. Color
        self.color_widget = QWidget()
        color_lay = QVBoxLayout(self.color_widget)
        color_lay.setContentsMargins(0,0,0,0)
        self.pick_color_btn = QPushButton("Pick Color & Auto-Set Range")
        self.pick_color_btn.clicked.connect(self.open_color_picker)
        color_lay.addWidget(self.pick_color_btn)
        
        self.h_min_slider = self.create_slider("Hue Min", 0, 179, 0, color_lay)
        self.h_max_slider = self.create_slider("Hue Max", 0, 179, 179, color_lay)
        self.s_min_slider = self.create_slider("Sat Min", 0, 255, 0, color_lay)
        self.s_max_slider = self.create_slider("Sat Max", 0, 255, 255, color_lay)
        self.v_min_slider = self.create_slider("Val Min", 0, 255, 0, color_lay)
        self.v_max_slider = self.create_slider("Val Max", 0, 255, 255, color_lay)
        self.detect_box.add_widget(self.color_widget)
        
        layout.addWidget(self.detect_box)

        # General Filters Box
        self.filter_box = CollapsibleBox("General Filters")
        self.blur_slider = self.create_slider("Blur", 0, 20, 0, self.filter_box.content_layout)
        self.dilate_slider = self.create_slider("Dilation", 0, 20, 0, self.filter_box.content_layout)
        self.min_area_slider = self.create_slider("Min Area", 10, 10000, 100, self.filter_box.content_layout)
        self.max_area_slider = self.create_slider("Max Area", 100, 100000, 50000, self.filter_box.content_layout)
        layout.addWidget(self.filter_box)

        # Export Button
        layout.addStretch() 
        self.export_btn = QPushButton("Export Video")
        self.export_btn.clicked.connect(self.export_requested)
        self.export_btn.setStyleSheet("background-color: #2e7d32; color: white; padding: 10px;") # Updated to Green
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        # Finish Setup
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # Expand meaningful sections by default
        self.detect_box.expand()
        self.vis_box.collapse()
        self.filter_box.collapse()

        # Initialize visibility based on default
        self.on_mode_changed(self.mode_combo.currentText())

    def create_slider(self, label_text, min_val, max_val, default, parent_layout):
        container = QWidget()
        lay = QVBoxLayout(container) # Vertical layout for safer resizing
        lay.setContentsMargins(0, 5, 0, 5)
        lay.setSpacing(2)
        
        # Top Row: Label ... Value
        top_row = QWidget()
        top_lay = QHBoxLayout(top_row)
        top_lay.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(label_text)
        top_lay.addWidget(lbl)
        
        val_lbl = QLabel(str(default))
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_lay.addWidget(val_lbl)
        
        lay.addWidget(top_row)
        
        # Slider Row
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(self.emit_params)
        slider.valueChanged.connect(lambda v, vl=val_lbl: vl.setText(str(v)))
        lay.addWidget(slider)
        
        if isinstance(parent_layout, QVBoxLayout) or isinstance(parent_layout, QHBoxLayout):
            parent_layout.addWidget(container)
        else:
            # Fallback if parent_layout is some other layout manager or we need to add differently
            parent_layout.addWidget(container)
            
        return slider

    def get_params(self):
        return {
            "mode": self.mode_combo.currentText(),
            "min_area": self.min_area_slider.value(),
            "max_area": self.max_area_slider.value(),
            "dilation": self.dilate_slider.value(),
            "blur": self.blur_slider.value(),
            "threshold": self.thresh_slider.value(),
            "canny_low": self.canny_low_slider.value(),
            "canny_high": self.canny_high_slider.value(),
            "h_min": self.h_min_slider.value(),
            "h_max": self.h_max_slider.value(),
            "s_min": self.s_min_slider.value(),
            "s_max": self.s_max_slider.value(),
            "v_min": self.v_min_slider.value(),
            "v_max": self.v_max_slider.value(),
        }

    def get_visual_settings(self):
        return {
            "color_mode": self.color_combo.currentText(),
            "text_mode": self.text_combo.currentText(),
            "shape_style": self.shape_combo.currentText(),
            "fixed_size_enabled": self.fixed_size_chk.isChecked(),
            "fixed_size": self.size_spin.value(),
            "show_dot": self.dot_chk.isChecked()
        }

    def emit_visuals(self):
        self.visuals_changed.emit(self.get_visual_settings())
        # Also emit basic shape for legacy listeners if needed
        self.shape_changed.emit(self.shape_combo.currentText())

    def emit_params(self):
        self.params_changed.emit(self.get_params())

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov)")
        if fname:
            self.file_label.setText(fname)
            self.export_btn.setEnabled(True)
            self.file_selected.emit(fname)

    def on_mode_changed(self, mode):
        # mode is string from combo
        self.gray_widget.setVisible(mode == DetectionMode.GRAYSCALE.value)
        self.edge_widget.setVisible(mode == DetectionMode.EDGES.value)
        self.color_widget.setVisible(mode == DetectionMode.COLOR.value)
        self.emit_params()

    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            h, s, v, _ = color.getHsv()
            h = int(h / 2)
            tol = 20
            self.h_min_slider.setValue(max(0, h - tol))
            self.h_max_slider.setValue(min(179, h + tol))
            self.s_min_slider.setValue(max(0, s - 50))
            self.s_max_slider.setValue(255)
            self.v_min_slider.setValue(max(0, v - 50))
            self.v_max_slider.setValue(255)
