import os # Added import
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QToolBar, 
                             QSizePolicy, QLabel) # Added QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon # Added import
from src.core.video_processor import VideoProcessor
from src.ui.widgets.control_panel import ControlPanel
from src.ui.widgets.video_player import VideoPlayer
from src.ui.themes import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blob Tracking Processor")
        self.resize(1000, 700) # Adjusted size
        
        self.processor = None
        self.dark_mode = True
        
        self.init_ui()
        self.apply_theme() # Initial theme application moved here

    def init_ui(self):
        # Set Window Icon
        icon_path = os.path.join(os.getcwd(), "src", "assets", "logo_blobtrack.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Control Panel
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel, stretch=1)

        # Video Player
        self.video_player = VideoPlayer()
        main_layout.addWidget(self.video_player, stretch=3)

        # Toolbar
        self.init_toolbar()

        # Connect Signals
        self.connect_signals()

    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # App Title in Toolbar
        title_label = QLabel("  BlobTrack  ")
        title_label.setObjectName("ToolbarTitle") 
        toolbar.addWidget(title_label)

        # Spacer (Before buttons)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)

        # Theme Toggle
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)
        
        # Exit Button
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        toolbar.addAction(exit_action)

    def connect_signals(self):
        self.control_panel.file_selected.connect(self.start_preview)
        self.control_panel.params_changed.connect(self.update_processor_params)
        self.control_panel.shape_changed.connect(self.update_shape)
        self.control_panel.visuals_changed.connect(self.update_visual_settings) # Connect new signal
        self.control_panel.export_requested.connect(self.start_export)
        
        self.video_player.toggle_play_requested.connect(self.toggle_video_pause)
        self.video_player.seek_requested.connect(self.seek_video)
        self.video_player.debug_toggled.connect(self.toggle_debug)
        self.video_player.file_selection_requested.connect(self.control_panel.select_file)

    def start_preview(self, path):
        if self.processor:
            self.processor.stop()
            self.processor.wait()
        
        shape = self.control_panel.shape_combo.currentText()
        self.processor = VideoProcessor(path, shape)
        self.processor.is_preview = True
        
        # Connect Signals
        self.processor.frame_update.connect(self.video_player.update_image)
        self.processor.duration_changed.connect(self.video_player.set_duration)
        self.processor.current_frame_changed.connect(self.video_player.update_position)
        
        # Init Params & Visuals
        self.update_processor_params(self.control_panel.get_params())
        self.update_visual_settings(self.control_panel.get_visual_settings())
        
        self.control_panel.emit_params() 
        self.control_panel.emit_visuals() # Ensure visuals are synced
        
        self.processor.start()
        self.video_player.image_label.setText("Loading...")
        self.video_player.setFocus() # Ensure it captures keys

    def start_export(self):
        if self.processor:
            self.processor.stop()
            self.processor.wait()
        
        path = self.control_panel.file_label.text() # Using raw label text, ideally store property
        shape = self.control_panel.shape_combo.currentText()
        
        self.processor = VideoProcessor(path, shape)
        self.processor.is_preview = False
        self.control_panel.emit_params()
        self.control_panel.emit_visuals()
        
        self.processor.finished.connect(lambda msg: self.video_player.image_label.setText(msg))
        # We could add a progress dialog here.
        
        self.processor.start()
        self.video_player.image_label.setText("Exporting...")

    def update_processor_params(self, params):
        if self.processor:
            self.processor.update_params(params)

    def update_visual_settings(self, settings):
        if self.processor:
            self.processor.update_visuals(settings)

    def toggle_debug(self, enabled):
        if self.processor:
            self.processor.set_debug_mode(enabled)

    def update_shape(self, shape):
        # Legacy/Redundant if visuals cover it, but keeping for safety
        if self.processor:
            self.processor.shape_type = shape

    def toggle_video_pause(self):
        if self.processor:
            self.processor.toggle_pause()

    def seek_video(self, frame_idx):
        if self.processor:
            self.processor.seek(frame_idx)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        # We rely on ThemeManager to set stylesheets on the app instance
        if self.dark_mode:
            ThemeManager.apply_theme("dark")
        else:
            ThemeManager.apply_theme("light")
            
    def keyPressEvent(self, event):
        # Global key handler if focus is elsewhere but we want spacebar to work?
        # VideoPlayer handles its own focus.
        if event.key() == Qt.Key.Key_Space:
            self.video_player.emit_toggle_play()
        else:
            super().keyPressEvent(event)
