from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                             QHBoxLayout, QPushButton, QSizePolicy, QButtonGroup,
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent, QSize
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter, QColor, QPainterPath

class VideoPlayer(QWidget):
    toggle_play_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    debug_toggled = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.is_playing = True
        self.total_frames = 0
        self.updating_slider = False # Prevent seeking emit while updating from video
        self.is_seeking = False # Track manual seeking state
        
        # Hover handling
        self.setMouseTracking(True)
        self.controls_visible = True
        self.hide_timer_active = False
        
        self.init_ui()

    def get_icon(self, name):
        # fast simple custom icons using QPainter
        pix = QPixmap(24, 24)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ffffff"))
        
        if name == "play":
            # Draw Triangle
            path = QPainterPath()
            path.moveTo(8, 5)
            path.lineTo(19, 12)
            path.lineTo(8, 19)
            path.closeSubpath()
            painter.drawPath(path)
        elif name == "pause":
            # Draw Bars
            painter.drawRoundedRect(6, 5, 4, 14, 2, 2)
            painter.drawRoundedRect(14, 5, 4, 14, 2, 2)
            
        painter.end()
        return QIcon(pix)

    def init_ui(self):
        # Use a layout that fills the whole widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Container for Video + Overlay
        self.video_container = QWidget()
        self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.video_container)
        
        self.video_layout = QVBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(0,0,0,0)
        self.video_layout.setSpacing(0)
        
        # Video Label
        self.image_label = QLabel("No Video Loaded")
        self.image_label.setObjectName("VideoDisplay")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.video_layout.addWidget(self.image_label)

        # OVERLAY CONTROLS
        self.overlay_widget = QWidget(self.video_container)
        self.overlay_widget.setObjectName("OverlayControls")
        self.overlay_widget.setStyleSheet("""
            QWidget#OverlayControls {
                background-color: rgba(20, 20, 20, 0.90); 
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            QLabel { color: #fff; font-weight: 600; font-family: "Segoe UI"; }
        """)
        
        # Opacity Effect for Fade
        self.opacity_effect = QGraphicsOpacityEffect(self.overlay_widget)
        self.opacity_effect.setOpacity(0.0) # Start hidden
        self.overlay_widget.setGraphicsEffect(self.opacity_effect)
        
        # Animation
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(200)

        # Overlay Layout
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.setContentsMargins(15, 10, 15, 10)

        # Top Row of Overlay (Video/Debug Toggle)
        top_row = QHBoxLayout()
        top_row.addStretch()
        
        self.view_group = QButtonGroup(self)
        self.btn_video = QPushButton("Video")
        self.btn_video.setCheckable(True)
        self.btn_video.setChecked(True)
        self.btn_debug = QPushButton("Debug")
        self.btn_debug.setCheckable(True)
        
        toggle_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #43a047;
                padding: 4px 12px;
                color: #ddd;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #2e7d32;
                color: #fff;
                font-weight: bold;
            }
        """
        self.btn_video.setStyleSheet(toggle_style)
        self.btn_debug.setStyleSheet(toggle_style)
        
        self.view_group.addButton(self.btn_video)
        self.view_group.addButton(self.btn_debug)
        self.view_group.buttonClicked.connect(self.on_view_changed)

        # Bottom Controls Layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.get_icon("pause")) # Default to playing state
        self.play_btn.setIconSize(QSize(20, 20))
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.1); }
        """)
        self.play_btn.clicked.connect(self.emit_toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        self.time_label = QLabel("0:00 / 0:00")
        controls_layout.addWidget(self.time_label)

        # Scrubber
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.setMouseTracking(True)
        self.slider.mousePressEvent = self.slider_mouse_press
        self.slider.mouseMoveEvent = self.slider_mouse_move
        self.slider.mouseReleaseEvent = self.slider_mouse_release
        controls_layout.addWidget(self.slider)

        # Add Debug Toggle to Right
        controls_layout.addWidget(self.btn_video)
        controls_layout.addWidget(self.btn_debug)

        overlay_layout.addLayout(controls_layout)

    def resizeEvent(self, event):
        # Reposition overlay to bottom
        if hasattr(self, 'overlay_widget'):
            w = self.width()
            h = 60 # Height of controls
            self.overlay_widget.setGeometry(0, self.height() - h, w, h)
        super().resizeEvent(event)

    def enterEvent(self, event):
        self.show_controls()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hide_controls()
        super().leaveEvent(event)

    def show_controls(self):
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(1.0)
        self.anim.start()

    def hide_controls(self):
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(0.0)
        self.anim.start()

    def on_view_changed(self, btn):
        is_debug = (btn == self.btn_debug)
        self.debug_toggled.emit(is_debug)

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
        # Critical Fix: Do not update slider if user is actively seeking
        if self.is_seeking:
            return
            
        if not self.slider.isSliderDown():
            self.updating_slider = True
            self.slider.setValue(frame_idx)
            self.updating_slider = False
            self.update_time_label(frame_idx)

    def update_time_label(self, current_frame):
        self.time_label.setText(f"{current_frame} / {self.total_frames}")

    def emit_toggle_play(self):
        self.toggle_play_requested.emit()
        self.is_playing = not self.is_playing
        icon_name = "play" if not self.is_playing else "pause"
        self.play_btn.setIcon(self.get_icon(icon_name))

    def slider_mouse_press(self, event):
        # Jump to clicked position
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_seeking = True # Start seeking
            val = self.slider.minimum() + (self.slider.maximum() - self.slider.minimum()) * event.position().x() / self.slider.width()
            self.slider.setValue(int(val))
            self.seek_requested.emit(int(val))

    def slider_mouse_move(self, event):
        # Live seek while dragging
        if self.is_seeking:
            val = self.slider.minimum() + (self.slider.maximum() - self.slider.minimum()) * event.position().x() / self.slider.width()
            val = max(self.slider.minimum(), min(self.slider.maximum(), int(val)))
            self.slider.setValue(val)
            self.seek_requested.emit(val)

    def slider_mouse_release(self, event):
        self.is_seeking = False
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.emit_toggle_play()
        else:
            super().keyPressEvent(event)
