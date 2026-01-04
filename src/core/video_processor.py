import cv2
import numpy as np
import os
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt6.QtGui import QImage
from src.core.tracking import BlobDetector, CentroidTracker
from src.visuals import VisualStateManager, Visualizer
from src.visuals.strategies import (
    WhiteColorStrategy, RainbowColorStrategy, CycleColorStrategy,
    SolidColorStrategy, BreatheColorStrategy, RippleColorStrategy, FireworkColorStrategy,
    TrackedShapeStrategy, FixedShapeStrategy,
    NoTextStrategy, IndexTextStrategy, RandomWordStrategy
)
from src.core.enums import DetectionMode, ColorMode, ColorEffectType, TextMode, TextPosition

class VideoProcessor(QThread):
    progress_update = pyqtSignal(int)
    frame_update = pyqtSignal(QImage, QImage) # Main, Ambient
    finished = pyqtSignal(str)
    duration_changed = pyqtSignal(int) # Total frames
    current_frame_changed = pyqtSignal(int) # Current frame index
    
    def __init__(self, input_path, shape_type):
        super().__init__()
        self.input_path = input_path
        self.shape_type = shape_type
        self.is_running = True
        self.is_paused = False
        self.is_preview = False
        self.debug_mode = False
        self.seek_req = -1
        
        self.mutex = QMutex()
        self.wait_cond = QWaitCondition()

        self.params = {
            "min_area": 100, "max_area": 100000,
            "dilation": 0, "blur": 0, "threshold": 127,
            "mode": DetectionMode.EDGES.value, # Default now Edges
            "canny_low": 50, "canny_high": 150,
            "h_min": 0, "s_min": 0, "v_min": 0,
            "h_max": 179, "s_max": 255, "v_max": 255
        }
        self.detector = BlobDetector()
        
        self.pending_visual_settings = None

    def update_visuals(self, settings):
        self.mutex.lock()
        self.pending_visual_settings = settings
        self.mutex.unlock()
    
    def _apply_visual_settings(self, visualizer, settings):
        # Color Mode Setup
        cm = settings.get("color_mode", ColorMode.SOLID.value)
        
        if cm == ColorMode.SOLID.value:
            solid_color = settings.get("solid_color", (255, 255, 255))
            visualizer.set_color_strategy(SolidColorStrategy(solid_color))
        elif cm == ColorMode.EFFECT.value:
            effect_name = settings.get("effect_name", ColorEffectType.RAINBOW.value)
            speed = settings.get("effect_speed", 50)
            self._set_effect_strategy(visualizer, effect_name, speed, 75)
        elif cm == ColorMode.CUSTOM.value:
            effect_name = settings.get("effect_name", ColorEffectType.NONE.value)
            speed = settings.get("effect_speed", 50)
            intensity = settings.get("effect_intensity", 75)
            primary_color = settings.get("primary_color", (67, 160, 71))
            self._set_effect_strategy(visualizer, effect_name, speed, intensity, primary_color)
        else:
            # Fallback
            visualizer.set_color_strategy(WhiteColorStrategy())
            
        # Text Settings
        tm = settings.get("text_mode", TextMode.NONE.value)
        if tm == TextMode.NONE.value:
            visualizer.set_text_strategy(NoTextStrategy())
        elif tm == TextMode.RANDOM_WORD.value:
            visualizer.set_text_strategy(RandomWordStrategy())
        else:  # Index or Custom
            visualizer.set_text_strategy(IndexTextStrategy())
        
        # Text styling 
        visualizer.text_size = settings.get("text_size", 14)
        visualizer.text_color = settings.get("text_color", (255, 255, 255))
        visualizer.text_position = settings.get("text_position", TextPosition.RIGHT.value)
            
        # Shape
        fixed = settings.get("fixed_size_enabled", False)
        if fixed:
            visualizer.set_shape_strategy(FixedShapeStrategy())
        else:
            visualizer.set_shape_strategy(TrackedShapeStrategy())
            
        visualizer.fixed_size = settings.get("fixed_size", 50)
        visualizer.show_center_dot = settings.get("show_dot", False)
        visualizer.fill_shape = settings.get("fill_shape", False)
        visualizer.fill_opacity = settings.get("fill_opacity", 0.5)
        
        # Overlays
        visualizer.show_traces = settings.get("show_traces", True)
        visualizer.border_thickness = settings.get("border_thickness", 2)
        
        # Tracer Settings
        visualizer.trace_thickness = settings.get("trace_thickness", 3)
        visualizer.trace_lifetime = settings.get("trace_lifetime", 20)
        trace_rgb = settings.get("trace_color", None)
        if trace_rgb:
            visualizer.trace_color = (trace_rgb[2], trace_rgb[1], trace_rgb[0])  # RGB to BGR
        else:
            visualizer.trace_color = None
        
        # Limits
        visualizer.max_blobs = settings.get("max_blobs", 50)
    
    def _set_effect_strategy(self, visualizer, effect_name, speed, intensity, primary_color=None):
        if effect_name == ColorEffectType.RAINBOW.value:
            visualizer.set_color_strategy(RainbowColorStrategy())
        elif effect_name == ColorEffectType.CYCLE.value:
            visualizer.set_color_strategy(CycleColorStrategy(speed=speed))
        elif effect_name == ColorEffectType.BREATHE.value:
            base = primary_color if primary_color else (67, 160, 71)
            visualizer.set_color_strategy(BreatheColorStrategy(base_color=base, speed=speed, intensity=intensity))
        elif effect_name == ColorEffectType.RIPPLE.value:
            visualizer.set_color_strategy(RippleColorStrategy(speed=speed, intensity=intensity))
        elif effect_name == ColorEffectType.FIREWORK.value:
            visualizer.set_color_strategy(FireworkColorStrategy(speed=speed, intensity=intensity))
        else:
            visualizer.set_color_strategy(WhiteColorStrategy())


    def update_params(self, params):
        self.params = params
        self.detector.update_params(params)

    def set_debug_mode(self, enabled):
        self.debug_mode = enabled

    def toggle_pause(self):
        self.mutex.lock()
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self.wait_cond.wakeAll()
        self.mutex.unlock()

    def seek(self, frame_idx):
        self.mutex.lock()
        self.seek_req = frame_idx
        self.wait_cond.wakeAll() # Wake if paused to process seek
        self.mutex.unlock()

    def run(self):
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            self.finished.emit("Error: Could not open video.")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        self.duration_changed.emit(total_frames)

        out = None
        if not self.is_preview:
            base, ext = os.path.splitext(self.input_path)
            output_path = f"{base}_tracked.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        self.detector.update_params(self.params)
        
        tracker = CentroidTracker()
        visual_state = VisualStateManager()
        visualizer = Visualizer(visual_state)
        frame_idx = 0
        
        while self.is_running:
            # Handle Pausing
            self.mutex.lock()
            if self.is_paused and self.seek_req == -1 and self.is_preview:
                self.wait_cond.wait(self.mutex)
            
            # Handle Seeking
            if self.seek_req != -1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_req)
                frame_idx = self.seek_req
                self.seek_req = -1
            self.mutex.unlock()

            ret, frame = cap.read()
            if not ret:
                if self.is_preview:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_idx = 0
                    continue
                else:
                    break

            # --- AMBIENT FRAME GENERATION (RAW) ---
            # Only generate for preview to save processing during export
            qt_ambient = None
            if self.is_preview:
                amb_small = cv2.resize(frame, (40, 22), interpolation=cv2.INTER_AREA)
                amb_blurred = cv2.GaussianBlur(amb_small, (21, 21), 0)
                amb_rgb = cv2.cvtColor(amb_blurred, cv2.COLOR_BGR2RGB)
                ah, aw, ach = amb_rgb.shape
                amb_bytes = ach * aw
                qt_ambient = QImage(amb_rgb.data, aw, ah, amb_bytes, QImage.Format.Format_RGB888).copy()

            # --- MAIN DETECTION & TRACKING ---
            # Detection
            rects, _, detection_data = self.detector.detect(frame)
            if isinstance(detection_data, tuple):
                 thresh, debug_frames = detection_data
            else:
                 thresh = detection_data
                 debug_frames = {}

            # Check for visual settings updates
            self.mutex.lock()
            if self.pending_visual_settings:
                 self._apply_visual_settings(visualizer, self.pending_visual_settings)
                 self.pending_visual_settings = None
            self.mutex.unlock()

            # Tracking
            objects = tracker.update(rects)
            
            # Prepare Output
            if self.is_preview:
                if self.debug_mode:
                    # Show the most relevant debug frame
                    if 'dilated' in debug_frames:
                        debug_img = debug_frames['dilated']
                    elif 'color_mask' in debug_frames:
                        debug_img = debug_frames['color_mask']
                    elif 'edges' in debug_frames:
                         debug_img = debug_frames['edges']
                    elif 'threshold' in debug_frames:
                         debug_img = debug_frames['threshold']
                    else:
                         debug_img = thresh
                    
                    if len(debug_img.shape) == 2:
                        out_frame = cv2.cvtColor(debug_img, cv2.COLOR_GRAY2BGR)
                    else:
                        out_frame = debug_img
                else:
                    out_frame = visualizer.draw(frame, objects, shape_type=self.shape_type, frame_idx=frame_idx)

                # Convert for Qt (BGR -> RGB)
                rgb_image = cv2.cvtColor(out_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                
                # COPY the data to ensure it persists
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
                self.frame_update.emit(qt_image, qt_ambient)
            
            self.current_frame_changed.emit(frame_idx)

            if not self.is_preview and out:
                # During export, always draw a clean frame (respecting current visualization settings)
                clean_frame = visualizer.draw(frame, objects, shape_type=self.shape_type, frame_idx=frame_idx)
                out.write(clean_frame)
                
                # Emit progress less frequently if needed, but 1% granularity is fine
                progress = int((frame_idx / total_frames) * 100)
                self.progress_update.emit(progress)

            frame_idx += 1
            
            # Simple FPS limiting for preview if needed, but Qt event loop handles it okay mostly.
            # actually for tight loops without GUI interaction we might need a tiny sleep?
            # self.msleep(int(1000/fps)) # Optional

        cap.release()
        if out:
            out.release()
            
        if not self.is_preview:
            filename = os.path.basename(output_path)
            self.finished.emit(f"Processing complete! Saved as {filename}")

    def stop(self):
        self.is_running = False
        self.mutex.lock()
        self.wait_cond.wakeAll()
        self.mutex.unlock()
