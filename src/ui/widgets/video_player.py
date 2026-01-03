from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                             QHBoxLayout, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

class VideoPlayer(QWidget):
    toggle_play_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_playing = True
        self.total_frames = 0
        self.updating_slider = False # Prevent seeking emit while updating from video

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video Display
        self.image_label = QLabel("No Video Loaded")
        self.image_label.setObjectName("VideoDisplay")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Style sheet removed here, handled by Global Theme
        # self.image_label.setStyleSheet("background-color: #000; color: #555;") 
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, 
            QSizePolicy.Policy.Ignored
        )
        layout.addWidget(self.image_label, stretch=1)

        # Controls Container
        controls_layout = QHBoxLayout()
        
        # Play/Pause
        self.play_btn = QPushButton("Pause")
        self.play_btn.clicked.connect(self.emit_toggle_play)
        controls_layout.addWidget(self.play_btn)

        # Timeline Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        # Enable clicking anywhere on the slider to jump
        self.slider.setMouseTracking(True)
        self.slider.mousePressEvent = self.slider_mouse_press
        self.slider.mouseMoveEvent = self.slider_mouse_move
        self.slider.mouseReleaseEvent = self.slider_mouse_release
        controls_layout.addWidget(self.slider)

        self.time_label = QLabel("0:00 / 0:00")
        controls_layout.addWidget(self.time_label)

        layout.addLayout(controls_layout)

    def update_image(self, qimg):
        # Scale to fit label, keep aspect ratio
        if self.image_label.size().width() > 0 and self.image_label.size().height() > 0:
            scaled = qimg.scaled(self.image_label.size(), 
                               Qt.AspectRatioMode.KeepAspectRatio, 
                               Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(QPixmap.fromImage(scaled))

    def set_duration(self, total_frames):
        self.total_frames = total_frames
        self.slider.setRange(0, total_frames)
    
    def update_position(self, frame_idx):
        if not self.slider.isSliderDown():
            self.updating_slider = True
            self.slider.setValue(frame_idx)
            self.updating_slider = False
            self.update_time_label(frame_idx)

    def update_time_label(self, current_frame):
        # Assuming 30fps roughly for label if we don't have exact fps easily available here
        # or we could pass fps too. For now frame count is fine.
        # Let's say Frame: X / Y
        self.time_label.setText(f"{current_frame} / {self.total_frames}")

    def emit_toggle_play(self):
        self.toggle_play_requested.emit()
        self.is_playing = not self.is_playing
        self.play_btn.setText("Play" if not self.is_playing else "Pause")

    def slider_mouse_press(self, event):
        # Jump to clicked position
        if event.button() == Qt.MouseButton.LeftButton:
            value = self.slider.minimum() + (self.slider.maximum() - self.slider.minimum()) * event.position().x() / self.slider.width()
            self.slider.setValue(int(value))
            self.seek_requested.emit(int(value))
            self.is_seeking = True

    def slider_mouse_move(self, event):
        # Live seek while dragging
        if hasattr(self, 'is_seeking') and self.is_seeking:
            value = self.slider.minimum() + (self.slider.maximum() - self.slider.minimum()) * event.position().x() / self.slider.width()
            value = max(self.slider.minimum(), min(self.slider.maximum(), int(value)))
            self.slider.setValue(value)
            self.seek_requested.emit(value)

    def slider_mouse_release(self, event):
        self.is_seeking = False
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.emit_toggle_play()
        else:
            super().keyPressEvent(event)
