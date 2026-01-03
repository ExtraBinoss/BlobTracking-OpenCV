from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QSlider, QLabel, QPushButton, QFileDialog, QHBoxLayout,
                             QScrollArea, QCheckBox, QColorDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.enums import DetectionMode, VisualStyle

class ControlPanel(QWidget):
    params_changed = pyqtSignal(dict)
    file_selected = pyqtSignal(str)
    export_requested = pyqtSignal()
    debug_toggled = pyqtSignal(bool) # Keeping signal for now if useful, but button is moving
    shape_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        # File Selection
        layout.addStretch() # Top stretch for vertical centering
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("border: 1px solid #555; padding: 5px;")
        btn_file = QPushButton("Select Video")
        btn_file.clicked.connect(self.select_file)
        layout.addWidget(btn_file)
        layout.addWidget(self.file_label)
        layout.addWidget(QLabel("<hr>"))

        # Visual Config
        vis_box = QGroupBox("Visual Style")
        vis_lay = QVBoxLayout()
        vis_lay.addWidget(QLabel("Shape:"))
        self.shape_combo = QComboBox()
        # Use Enums
        self.shape_combo.addItems([e.value for e in VisualStyle])
        self.shape_combo.currentTextChanged.connect(lambda t: self.shape_changed.emit(t))
        vis_lay.addWidget(self.shape_combo)
        vis_box.setLayout(vis_lay)
        layout.addWidget(vis_box)
        
        # Debug View Toggle REMOVED (Moved to VideoPlayer)

        # Detection Mode
        mode_box = QGroupBox("Detection Mode")
        mode_lay = QVBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([e.value for e in DetectionMode])
        self.mode_combo.setCurrentText(DetectionMode.EDGES.value) # Default to Edges
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_lay.addWidget(self.mode_combo)
        mode_box.setLayout(mode_lay)
        layout.addWidget(mode_box)

        # Shared Settings
        shared_box = QGroupBox("General Filters")
        shared_lay = QVBoxLayout()
        self.blur_slider = self.create_slider("Blur", 0, 20, 0, shared_lay)
        self.dilate_slider = self.create_slider("Dilation", 0, 20, 0, shared_lay)
        self.min_area_slider = self.create_slider("Min Area", 10, 10000, 100, shared_lay)
        self.max_area_slider = self.create_slider("Max Area", 100, 100000, 50000, shared_lay)
        shared_box.setLayout(shared_lay)
        layout.addWidget(shared_box)

        # Mode Specific: Grayscale
        self.gray_group = QGroupBox("Grayscale Settings")
        gray_lay = QVBoxLayout()
        self.thresh_slider = self.create_slider("Threshold", 0, 255, 127, gray_lay)
        self.gray_group.setLayout(gray_lay)
        layout.addWidget(self.gray_group)

        # Mode Specific: Edges
        self.edge_group = QGroupBox("Edge (Canny) Settings")
        edge_lay = QVBoxLayout()
        self.canny_low_slider = self.create_slider("Low Threshold", 0, 255, 50, edge_lay)
        self.canny_high_slider = self.create_slider("High Threshold", 0, 255, 150, edge_lay)
        self.edge_group.setLayout(edge_lay)
        layout.addWidget(self.edge_group)

        # Mode Specific: Color
        self.color_group = QGroupBox("Color (HSV) Settings")
        color_lay = QVBoxLayout()
        self.pick_color_btn = QPushButton("Pick Color & Auto-Set Range")
        self.pick_color_btn.clicked.connect(self.open_color_picker)
        color_lay.addWidget(self.pick_color_btn)
        
        self.h_min_slider = self.create_slider("Hue Min", 0, 179, 0, color_lay)
        self.h_max_slider = self.create_slider("Hue Max", 0, 179, 179, color_lay)
        self.s_min_slider = self.create_slider("Sat Min", 0, 255, 0, color_lay)
        self.s_max_slider = self.create_slider("Sat Max", 0, 255, 255, color_lay)
        self.v_min_slider = self.create_slider("Val Min", 0, 255, 0, color_lay)
        self.v_max_slider = self.create_slider("Val Max", 0, 255, 255, color_lay)
        self.color_group.setLayout(color_lay)
        layout.addWidget(self.color_group)

        # Export Button
        # Removed addStretch to allow top alignment if outer layout handles it, 
        # or keep it if we want buttons at bottom. 
        # User complained about "not put on the middle". 
        # Using a centered layout in MainWindow is better, so we'll just let this fill naturally.
        # But commonly we want control contents at top.
        layout.addStretch() 

        self.export_btn = QPushButton("Export Video")
        self.export_btn.clicked.connect(self.export_requested)
        self.export_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        # Finish Setup
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # Initialize visibility based on default
        self.on_mode_changed(self.mode_combo.currentText())

    def create_slider(self, label_text, min_val, max_val, default, parent_layout):
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(8)
        
        lbl = QLabel(f"{label_text}:")
        lbl.setFixedWidth(80)
        lay.addWidget(lbl)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.setMinimumHeight(20)
        slider.valueChanged.connect(lambda v, l=lbl, txt=label_text: l.setText(f"{txt}:"))
        slider.valueChanged.connect(self.emit_params)
        lay.addWidget(slider, stretch=1)
        
        val_lbl = QLabel(str(default))
        val_lbl.setFixedWidth(50)
        slider.valueChanged.connect(lambda v, vl=val_lbl: vl.setText(str(v)))
        lay.addWidget(val_lbl)
        
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
        self.gray_group.setVisible(mode == DetectionMode.GRAYSCALE.value)
        self.edge_group.setVisible(mode == DetectionMode.EDGES.value)
        self.color_group.setVisible(mode == DetectionMode.COLOR.value)
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
