from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QPushButton
from PyQt6.QtCore import Qt
from src.core.video_processor import VideoProcessor
from src.ui.widgets.control_panel import ControlPanel
from src.ui.widgets.video_player import VideoPlayer
from src.ui.themes import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blob Tracking Processor")
        self.resize(1200, 800)
        
        self.processor = None
        self.dark_mode = True
        
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Widgets
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(380)
        
        self.video_player = VideoPlayer()

        # Layout
        main_layout.addWidget(self.control_panel)
        main_layout.addWidget(self.video_player, stretch=1)
        
        # Theme Toggle (Floating or Top Bar? Placing in layout for now)
        # We can add it to the top of control panel, but let's just make it a corner button or similar.
        # Actually proper way: add a Menu Bar or Toolbar.
        toolbar = self.addToolBar("Helpers")
        
        theme_action = toolbar.addAction("Toggle Theme")
        theme_action.triggered.connect(self.toggle_theme)

        # Connections
        self.control_panel.file_selected.connect(self.start_preview)
        self.control_panel.params_changed.connect(self.update_processor_params)
        self.control_panel.debug_toggled.connect(self.toggle_debug)
        self.control_panel.shape_changed.connect(self.update_shape)
        self.control_panel.export_requested.connect(self.start_export)
        
        self.video_player.toggle_play_requested.connect(self.toggle_video_pause)
        self.video_player.seek_requested.connect(self.seek_video)

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
        
        # Init Params
        self.update_processor_params(self.control_panel.get_params())
        # Wait, emit_params returns nothing, it emits signal. We need `get_current_params` logic or just rely on signal.
        # Let's fix ControlPanel to trigger initial emission or store state.
        # Actually `ControlPanel.emit_params` emits the signal.
        self.control_panel.emit_params() 
        
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
        
        self.processor.finished.connect(lambda msg: self.video_player.image_label.setText(msg))
        # We could add a progress dialog here.
        
        self.processor.start()
        self.video_player.image_label.setText("Exporting...")

    def update_processor_params(self, params):
        if self.processor:
            self.processor.update_params(params)

    def toggle_debug(self, enabled):
        if self.processor:
            self.processor.set_debug_mode(enabled)

    def update_shape(self, shape):
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
        app = QApplication.instance()
        if self.dark_mode:
            app.setPalette(ThemeManager.get_dark_palette())
            # Fix style sheet clashes for standard widgets if any
        else:
            app.setPalette(ThemeManager.get_light_palette())
            
    def keyPressEvent(self, event):
        # Global key handler if focus is elsewhere but we want spacebar to work?
        # VideoPlayer handles its own focus.
        if event.key() == Qt.Key.Key_Space:
            self.video_player.emit_toggle_play()
        else:
            super().keyPressEvent(event)
