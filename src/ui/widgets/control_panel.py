from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QSlider, QLabel, QPushButton, QFileDialog, QHBoxLayout,
                             QTabWidget, QCheckBox, QColorDialog, QSpinBox, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.enums import DetectionMode, VisualStyle
from src.ui.widgets.custom_combo import ClickableComboBox

class ControlPanel(QWidget):
    params_changed = pyqtSignal(dict)
    file_selected = pyqtSignal(str)
    export_requested = pyqtSignal()
    debug_toggled = pyqtSignal(bool) 
    shape_changed = pyqtSignal(str)
    visuals_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: DETECTION ---
        self.tab_detect = QWidget()
        self.init_detection_tab()
        self.tabs.addTab(self.tab_detect, "Detection")
        
        # --- TAB 2: VISUALS ---
        self.tab_visuals = QWidget()
        self.init_visuals_tab()
        self.tabs.addTab(self.tab_visuals, "Visuals")
        
        # --- TAB 3: PROJECT ---
        self.tab_project = QWidget()
        self.init_project_tab()
        self.tabs.addTab(self.tab_project, "Project")

        # Initial State
        self.on_mode_changed(self.mode_combo.currentText())

    def init_detection_tab(self):
        layout = QVBoxLayout(self.tab_detect)
        layout.setSpacing(15)
        
        # 1. Mode Selection
        mode_group = QGroupBox("Detection Mode")
        mode_lay = QVBoxLayout(mode_group)
        self.mode_combo = ClickableComboBox()
        self.mode_combo.addItems([e.value for e in DetectionMode])
        self.mode_combo.setCurrentText(DetectionMode.EDGES.value)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_lay.addWidget(self.mode_combo)
        layout.addWidget(mode_group)
        
        # 2. Dynamic Settings Area
        self.dynamic_settings_group = QGroupBox("Mode Settings")
        dyn_lay = QVBoxLayout(self.dynamic_settings_group)
        
        # Grayscale Specs
        self.gray_widget = QWidget()
        g_lay = QVBoxLayout(self.gray_widget)
        g_lay.setContentsMargins(0,0,0,0)
        self.thresh_slider = self.create_slider("Threshold", 0, 255, 127, g_lay)
        dyn_lay.addWidget(self.gray_widget)
        
        # Edge Specs
        self.edge_widget = QWidget()
        e_lay = QVBoxLayout(self.edge_widget)
        e_lay.setContentsMargins(0,0,0,0)
        self.canny_low_slider = self.create_slider("Low Threshold", 0, 255, 50, e_lay)
        self.canny_high_slider = self.create_slider("High Threshold", 0, 255, 150, e_lay)
        dyn_lay.addWidget(self.edge_widget)
        
        # Color Specs
        self.color_widget = QWidget()
        c_lay = QVBoxLayout(self.color_widget)
        c_lay.setContentsMargins(0,0,0,0)
        self.pick_color_btn = QPushButton("Pick Target Color")
        self.pick_color_btn.clicked.connect(self.open_color_picker)
        c_lay.addWidget(self.pick_color_btn)
        
        # Compact HSV Sliders
        self.h_min_slider = self.create_slider("H Min", 0, 179, 0, c_lay)
        self.h_max_slider = self.create_slider("H Max", 0, 179, 179, c_lay)
        self.s_min_slider = self.create_slider("S Min", 0, 255, 0, c_lay)
        self.s_max_slider = self.create_slider("S Max", 0, 255, 255, c_lay)
        self.v_min_slider = self.create_slider("V Min", 0, 255, 0, c_lay)
        self.v_max_slider = self.create_slider("V Max", 0, 255, 255, c_lay)
        dyn_lay.addWidget(self.color_widget)
        
        layout.addWidget(self.dynamic_settings_group)
        
        # 3. General Filters
        filter_group = QGroupBox("Pre-processing & Filters")
        f_lay = QVBoxLayout(filter_group)
        self.blur_slider = self.create_slider("Blur", 0, 20, 0, f_lay)
        self.dilate_slider = self.create_slider("Dilation", 0, 20, 0, f_lay)
        self.min_area_slider = self.create_slider("Min Area", 10, 10000, 100, f_lay)
        self.max_area_slider = self.create_slider("Max Area", 100, 100000, 50000, f_lay)
        layout.addWidget(filter_group)
        
        layout.addStretch()

    def init_visuals_tab(self):
        layout = QVBoxLayout(self.tab_visuals)
        layout.setSpacing(15)
        
        # Style
        style_group = QGroupBox("Style")
        s_lay = QFormLayout(style_group)
        
        self.shape_combo = ClickableComboBox()
        self.shape_combo.addItems([e.value for e in VisualStyle])
        self.shape_combo.currentTextChanged.connect(self.emit_visuals)
        s_lay.addRow("Shape:", self.shape_combo)
        
        self.color_combo = ClickableComboBox()
        self.color_combo.addItems(["White", "Rainbow", "Cycle"])
        self.color_combo.currentTextChanged.connect(self.emit_visuals)
        s_lay.addRow("Color:", self.color_combo)
        
        self.text_combo = ClickableComboBox()
        self.text_combo.addItems(["None", "Index", "Random Word"])
        self.text_combo.currentTextChanged.connect(self.emit_visuals)
        s_lay.addRow("Text:", self.text_combo)
        
        self.text_pos_combo = ClickableComboBox()
        self.text_pos_combo.addItems(["Right", "Top", "Bottom", "Center"])
        self.text_pos_combo.currentTextChanged.connect(self.emit_visuals)
        s_lay.addRow("Text Pos:", self.text_pos_combo)
        
        layout.addWidget(style_group)
        
        # Geometry & Overlays
        geom_group = QGroupBox("Geometry & Overlays")
        g_lay = QVBoxLayout(geom_group)
        
        self.trace_chk = QCheckBox("Show Traces")
        self.trace_chk.setChecked(True)
        self.trace_chk.toggled.connect(self.emit_visuals)
        g_lay.addWidget(self.trace_chk)
        
        self.dot_chk = QCheckBox("Show Centroid Dot")
        self.dot_chk.setChecked(True)
        self.dot_chk.toggled.connect(self.emit_visuals)
        g_lay.addWidget(self.dot_chk)
        
        self.border_slider = self.create_slider("Border Thickness", 1, 10, 2, g_lay)
        self.border_slider.valueChanged.connect(self.emit_visuals)
        
        # Fixed Size
        fs_row = QHBoxLayout()
        self.fixed_size_chk = QCheckBox("Fixed Size")
        self.fixed_size_chk.toggled.connect(self.emit_visuals)
        fs_row.addWidget(self.fixed_size_chk)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 500)
        self.size_spin.setValue(50)
        self.size_spin.setSuffix(" px")
        self.size_spin.valueChanged.connect(self.emit_visuals)
        fs_row.addWidget(self.size_spin)
        g_lay.addLayout(fs_row)
        
        layout.addWidget(geom_group)
        layout.addStretch()

    def init_project_tab(self):
        layout = QVBoxLayout(self.tab_project)
        layout.setSpacing(20)
        
        # File Info
        info_group = QGroupBox("Input Source")
        i_lay = QVBoxLayout(info_group)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("border: 2px dashed #555; padding: 20px; border-radius: 8px;")
        i_lay.addWidget(self.file_label)
        
        btn_file = QPushButton("Select Video File")
        btn_file.setStyleSheet("padding: 8px;")
        btn_file.clicked.connect(self.select_file)
        i_lay.addWidget(btn_file)
        
        layout.addWidget(info_group)
        
        # Actions
        action_group = QGroupBox("Actions")
        a_lay = QVBoxLayout(action_group)
        
        self.export_btn = QPushButton("Export Processed Video")
        self.export_btn.clicked.connect(self.export_requested)
        self.export_btn.setStyleSheet("background-color: #2e7d32; color: white; padding: 12px; font-weight: bold;")
        self.export_btn.setEnabled(False)
        a_lay.addWidget(self.export_btn)
        
        layout.addWidget(action_group)
        layout.addStretch()

    def create_slider(self, label_text, min_val, max_val, default, parent_layout):
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 5, 0, 5)
        lay.setSpacing(2)
        
        top_row = QWidget()
        top_lay = QHBoxLayout(top_row)
        top_lay.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(label_text)
        top_lay.addWidget(lbl)
        
        val_lbl = QLabel(str(default))
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_lay.addWidget(val_lbl)
        
        lay.addWidget(top_row)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(self.emit_params)
        slider.valueChanged.connect(lambda v, vl=val_lbl: vl.setText(str(v)))
        lay.addWidget(slider)
        
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
            "show_dot": self.dot_chk.isChecked(),
            "show_traces": self.trace_chk.isChecked(),
            "border_thickness": self.border_slider.value(),
            "text_position": self.text_pos_combo.currentText()
        }

    def emit_visuals(self, *args):
        self.visuals_changed.emit(self.get_visual_settings())
        self.shape_changed.emit(self.shape_combo.currentText())

    def emit_params(self, *args):
        self.params_changed.emit(self.get_params())

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov)")
        if fname:
            self.file_label.setText(fname)
            self.export_btn.setEnabled(True)
            self.file_selected.emit(fname)

    def on_mode_changed(self, mode):
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
