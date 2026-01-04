from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QComboBox, 
                             QSlider, QLabel, QPushButton, QFileDialog, QHBoxLayout,
                             QTabWidget, QCheckBox, QColorDialog, QSpinBox, QFormLayout,
                             QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.core.enums import DetectionMode, VisualStyle
from src.ui.widgets.custom_combo import ClickableComboBox
from src.ui.widgets.color_effect_widget import ColorEffectWidget
from src.ui.widgets.text_style_widget import TextStyleWidget
from src.ui.widgets.color_picker_widget import CompactColorButton

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
        
        # --- TAB 1: DETECTION (with scroll) ---
        self.tab_detect_scroll = QScrollArea()
        self.tab_detect_scroll.setWidgetResizable(True)
        self.tab_detect = QWidget()
        self.tab_detect_scroll.setWidget(self.tab_detect)
        self.init_detection_tab()
        self.tabs.addTab(self.tab_detect_scroll, "Detection")
        
        # --- TAB 2: VISUALS (with scroll) ---
        self.tab_visuals_scroll = QScrollArea()
        self.tab_visuals_scroll.setWidgetResizable(True)
        self.tab_visuals = QWidget()
        self.tab_visuals_scroll.setWidget(self.tab_visuals)
        self.init_visuals_tab()
        self.tabs.addTab(self.tab_visuals_scroll, "Visuals")
        
        # --- TAB 3: PROJECT (with scroll) ---
        self.tab_project_scroll = QScrollArea()
        self.tab_project_scroll.setWidgetResizable(True)
        self.tab_project = QWidget()
        self.tab_project_scroll.setWidget(self.tab_project)
        self.init_project_tab()
        self.tabs.addTab(self.tab_project_scroll, "Project")

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
        
        # Color Specs (Simplified)
        self.color_detect_widget = QWidget()
        c_lay = QVBoxLayout(self.color_detect_widget)
        c_lay.setContentsMargins(0,0,0,0)
        c_lay.setSpacing(8)
        
        # Target Color Button
        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Target:"))
        self.target_color_btn = CompactColorButton(QColor(255, 0, 0))
        self.target_color_btn.colorChanged.connect(self.emit_params)
        target_row.addWidget(self.target_color_btn, 1)
        c_lay.addLayout(target_row)
        
        # Tolerance Slider
        self.tolerance_slider = self.create_slider("Tolerance", 5, 100, 30, c_lay)
        
        dyn_lay.addWidget(self.color_detect_widget)
        
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
        
        # Shape Selection (simple)
        shape_group = QGroupBox("Shape")
        shape_lay = QVBoxLayout(shape_group)
        
        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Style:"))
        self.shape_combo = ClickableComboBox()
        self.shape_combo.addItems([e.value for e in VisualStyle])
        self.shape_combo.currentTextChanged.connect(self.emit_visuals)
        shape_row.addWidget(self.shape_combo, 1)
        shape_lay.addLayout(shape_row)
        
        layout.addWidget(shape_group)
        
        # Color System (modular)
        color_group = QGroupBox("Color")
        color_lay = QVBoxLayout(color_group)
        self.color_widget = ColorEffectWidget()
        self.color_widget.settings_changed.connect(self.emit_visuals)
        color_lay.addWidget(self.color_widget)
        layout.addWidget(color_group)
        
        # Text System (modular)
        text_group = QGroupBox("Text")
        text_lay = QVBoxLayout(text_group)
        self.text_widget = TextStyleWidget()
        self.text_widget.settings_changed.connect(self.emit_visuals)
        text_lay.addWidget(self.text_widget)
        layout.addWidget(text_group)
        
        # --- TRACES GROUP ---
        trace_group = QGroupBox("Traces")
        t_lay = QVBoxLayout(trace_group)
        t_lay.setSpacing(8)
        
        self.trace_chk = QCheckBox("Show Traces")
        self.trace_chk.setChecked(True)
        self.trace_chk.toggled.connect(self.emit_visuals)
        t_lay.addWidget(self.trace_chk)
        
        self.trace_thickness_slider = self.create_slider("Thickness", 1, 10, 3, t_lay)
        self.trace_thickness_slider.valueChanged.connect(self.emit_visuals)
        
        self.trace_lifetime_slider = self.create_slider("Lifetime", 5, 60, 20, t_lay)
        self.trace_lifetime_slider.valueChanged.connect(self.emit_visuals)
        
        trace_color_row = QHBoxLayout()
        trace_color_row.addWidget(QLabel("Color:"))
        self.trace_color_btn = CompactColorButton(QColor(0, 255, 0))
        self.trace_color_btn.colorChanged.connect(self.emit_visuals)
        trace_color_row.addWidget(self.trace_color_btn, 1)
        t_lay.addLayout(trace_color_row)
        
        layout.addWidget(trace_group)
        
        # --- BLOBS GROUP ---
        blob_group = QGroupBox("Blobs")
        b_lay = QVBoxLayout(blob_group)
        b_lay.setSpacing(8)
        
        # Max Blobs
        max_row = QHBoxLayout()
        max_row.addWidget(QLabel("Max Count:"))
        self.max_blobs_spin = QSpinBox()
        self.max_blobs_spin.setRange(1, 100)
        self.max_blobs_spin.setValue(50)
        self.max_blobs_spin.valueChanged.connect(self.emit_visuals)
        max_row.addWidget(self.max_blobs_spin, 1)
        b_lay.addLayout(max_row)
        
        self.border_slider = self.create_slider("Border", 1, 10, 2, b_lay)
        self.border_slider.valueChanged.connect(self.emit_visuals)
        
        # Fill & Dot options
        opts_row = QHBoxLayout()
        
        # Fill Layout
        fill_col = QVBoxLayout()
        fill_col.setSpacing(0)
        
        self.fill_chk = QCheckBox("Fill Shape")
        self.fill_chk.setChecked(False) 
        self.fill_chk.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.fill_chk.toggled.connect(self.emit_visuals)
        self.fill_chk.toggled.connect(self.toggle_fill_opacity_slider)
        fill_col.addWidget(self.fill_chk)
        
        # Opacity Slider (create_slider adds to layout)
        self.fill_opacity_slider = self.create_slider("Fill Opacity", 0, 100, 50, fill_col)
        self.fill_opacity_slider.setVisible(False)
        self.fill_opacity_slider.valueChanged.connect(self.emit_visuals)
        
        opts_row.addLayout(fill_col)

        self.dot_chk = QCheckBox("Show Dot")
        self.dot_chk.setChecked(False) # Default No Dot
        self.dot_chk.toggled.connect(self.emit_visuals)
        opts_row.addWidget(self.dot_chk)
        
        b_lay.addLayout(opts_row)
        
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
        b_lay.addLayout(fs_row)
        
        layout.addWidget(blob_group)
        
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
        a_lay.setSpacing(10)
        
        self.export_btn = QPushButton("Export Processed Video")
        self.export_btn.setObjectName("PrimaryButton") # Use theme
        self.export_btn.clicked.connect(self.export_requested)
        self.export_btn.setEnabled(False)
        a_lay.addWidget(self.export_btn)
        
        # Open Location Button
        self.open_folder_btn = QPushButton("Open File Location")
        self.open_folder_btn.clicked.connect(self.open_file_location)
        self.open_folder_btn.setEnabled(False) 
        a_lay.addWidget(self.open_folder_btn)
        
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
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.valueChanged.connect(self.emit_params)
        slider.valueChanged.connect(lambda v, vl=val_lbl: vl.setText(str(v)))
        lay.addWidget(slider)
        
        parent_layout.addWidget(container)
        return slider

    def get_params(self):
        h_min, h_max, s_min, s_max, v_min, v_max = self._get_target_hsv_range()
        return {
            "mode": self.mode_combo.currentText(),
            "min_area": self.min_area_slider.value(),
            "max_area": self.max_area_slider.value(),
            "dilation": self.dilate_slider.value(),
            "blur": self.blur_slider.value(),
            "threshold": self.thresh_slider.value(),
            "canny_low": self.canny_low_slider.value(),
            "canny_high": self.canny_high_slider.value(),
            "h_min": h_min,
            "h_max": h_max,
            "s_min": s_min,
            "s_max": s_max,
            "v_min": v_min,
            "v_max": v_max,
        }

    def get_visual_settings(self):
        # Base settings
        settings = {
            "shape_style": self.shape_combo.currentText(),
            "fixed_size_enabled": self.fixed_size_chk.isChecked(),
            "fixed_size": self.size_spin.value(),
            "show_dot": self.dot_chk.isChecked(),
            "fill_shape": self.fill_chk.isChecked(),
            "fill_opacity": self.fill_opacity_slider.value() / 100.0,
            "show_traces": self.trace_chk.isChecked(),
            "border_thickness": self.border_slider.value(),
            "trace_thickness": self.trace_thickness_slider.value(),
            "trace_lifetime": self.trace_lifetime_slider.value(),
            "trace_color": self.trace_color_btn.getRGB(),
            "max_blobs": self.max_blobs_spin.value(),
        }
        
        # Merge color settings
        settings.update(self.color_widget.get_settings())
        
        # Merge text settings
        settings.update(self.text_widget.get_settings())
        
        return settings

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
        self.color_detect_widget.setVisible(mode == DetectionMode.COLOR.value)
        self.emit_params()
    
    def _get_target_hsv_range(self):
        """Convert target color button's color and tolerance to HSV range."""
        color = self.target_color_btn.getColor()
        h, s, v, _ = color.getHsv()
        h = int(h / 2)  # Qt uses 0-359, OpenCV uses 0-179
        tol = self.tolerance_slider.value()
        
        h_min = max(0, h - tol)
        h_max = min(179, h + tol)
        s_min = max(0, s - 50)
        s_max = 255
        v_min = max(0, v - 50)
        v_max = 255
        
        return h_min, h_max, s_min, s_max, v_min, v_max

    def open_file_location(self):
        import subprocess
        import os
        
        path = self.file_label.text()
        if not path or not os.path.exists(path):
            return
            
        export_path = f"{os.path.splitext(path)[0]}_processed.mp4"
        if not os.path.exists(export_path):
             # Try input dir if export doesn't exist
             folder = os.path.dirname(path)
        else:
             folder = os.path.dirname(export_path)
             
        # OS Agnostic Open
        if os.name == 'nt':
            subprocess.Popen(['explorer', folder])
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', folder])
        else:
             # Mac
            subprocess.Popen(['open', folder])

    def toggle_fill_opacity_slider(self, checked):
        self.fill_opacity_slider.setVisible(checked)
        # Force layout update if needed
        self.updateGeometry()
