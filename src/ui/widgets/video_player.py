from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                             QHBoxLayout, QPushButton, QSizePolicy, QButtonGroup,
                             QGraphicsOpacityEffect, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent, QSize
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter, QColor, QPainterPath

class VideoPlayer(QWidget):
    toggle_play_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)
    debug_toggled = pyqtSignal(bool)
    file_selection_requested = pyqtSignal()

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
        
        # Stacked Layout Logic: Grid or Stack? 
        # Grid allows overlapping if we put everything in (0,0).
        self.video_layout = QGridLayout(self.video_container)
        self.video_layout.setContentsMargins(0,0,0,0)
        self.video_layout.setSpacing(0)
        
        # Layer 0: Ambient Background (Stretched)
        self.ambient_label = QLabel()
        self.ambient_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.ambient_label.setScaledContents(True) # Hardware/Qt scaling of pixmap
        self.video_layout.addWidget(self.ambient_label, 0, 0)

        # 1. Main Video Display Label (Layer 0, on top of ambient)
        self.video_display_label = QLabel()
        self.video_display_label.setObjectName("MainVideoDisplay")
        self.video_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_display_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.video_layout.addWidget(self.video_display_label, 0, 0)

        # 2. Placeholder Container (Layer 1, Center Aligned, Visible initially)
        self.placeholder_widget = QWidget()
        self.placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_layout.setContentsMargins(0, 0, 0, 0)
        self.placeholder_layout.setSpacing(10) # Space between text and button
        self.placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Status Label (Top of placeholder)
        self.placeholder_label = QLabel("No Video Loaded")
        self.placeholder_label.setObjectName("PlaceholderLabel")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel#PlaceholderLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 18px;
                font-weight: 500;
                letter-spacing: 1px;
            }
        """)
        self.placeholder_layout.addWidget(self.placeholder_label)

        # Big Select Button (Bottom of placeholder)
        self.big_select_btn = QPushButton("Select Video File")
        self.big_select_btn.setObjectName("BigSelectButton")
        self.big_select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.big_select_btn.setFixedWidth(280) # Fixed width looks better in column
        self.big_select_btn.setStyleSheet("""
            QPushButton#BigSelectButton {
                font-size: 18px; 
                font-weight: bold;
                color: #66bb6a;
                background-color: transparent;
                border: 2px dashed #43a047;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton#BigSelectButton:hover {
                background-color: rgba(67, 160, 71, 0.1);
                border-style: solid;
            }
        """)
        self.big_select_btn.clicked.connect(self.file_selection_requested)
        self.placeholder_layout.addWidget(self.big_select_btn)

        # Add Placeholder Container to Grid (Centered)
        self.video_layout.addWidget(self.placeholder_widget, 0, 0, Qt.AlignmentFlag.AlignCenter)

        # OVERLAY CONTROLS
        self.overlay_widget = QWidget(self.video_container)
        self.overlay_widget.setObjectName("OverlayControls")
        self.overlay_widget.setStyleSheet("""
            QWidget#OverlayControls {
                background-color: rgba(20, 20, 20, 0.90); 
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
            QLabel { 
                color: #ffffff; 
                font-weight: 600; 
                font-family: "Segoe UI";
                background: transparent; 
            }
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
        self.btn_debug = QPushButton("Process")
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

    def update_image(self, qimg, ambient_qimg):
        # Hide Placeholder if it's visible
        if self.placeholder_widget.isVisible():
            self.placeholder_widget.setVisible(False)
            
        # OPTIMIZED AMBIENT:
        # Pre-processed ambient frame (small, blurred, raw) is provided
        self.ambient_label.setPixmap(QPixmap.fromImage(ambient_qimg))
        
        # Normal Video Update
        if self.video_display_label.size().width() > 0 and self.video_display_label.size().height() > 0:
            scaled = qimg.scaled(self.video_display_label.size(), 
                               Qt.AspectRatioMode.KeepAspectRatio, 
                               Qt.TransformationMode.SmoothTransformation)
            self.video_display_label.setPixmap(QPixmap.fromImage(scaled))

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
