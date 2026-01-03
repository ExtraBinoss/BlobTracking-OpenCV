import cv2
import numpy as np
import os
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt6.QtGui import QImage
from src.tracking import BlobDetector, CentroidTracker
from src.visuals import VisualStateManager, Visualizer

class VideoProcessor(QThread):
    progress_update = pyqtSignal(int)
    frame_update = pyqtSignal(QImage)
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
            "mode": "grayscale",
            "canny_low": 50, "canny_high": 150,
            "h_min": 0, "s_min": 0, "v_min": 0,
            "h_max": 179, "s_max": 255, "v_max": 255
        }
        self.detector = BlobDetector()

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

            # Detection
            rects, _, debug_thresh = self.detector.detect(frame)
            
            # Tracking
            objects = tracker.update(rects)
            
            # Prepare Output
            if self.is_preview and self.debug_mode:
                if len(debug_thresh.shape) == 2:
                    out_frame = cv2.cvtColor(debug_thresh, cv2.COLOR_GRAY2BGR)
                else:
                    out_frame = debug_thresh
            else:
                out_frame = visualizer.draw(frame, objects, shape=self.shape_type)

            # Convert for Qt (BGR -> RGB)
            rgb_image = cv2.cvtColor(out_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            # COPY the data to ensure it persists after the numpy array is garbage collected
            # Fixes Segmentation Fault
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
            
            self.frame_update.emit(qt_image)
            self.current_frame_changed.emit(frame_idx)

            if not self.is_preview and out:
                if self.debug_mode: # If debugging during export, re-draw "clean" for export?
                     # For now, export what is seen or force clean. 
                     # Usually export is clean.
                     clean_frame = visualizer.draw(frame, objects, shape=self.shape_type)
                     out.write(clean_frame)
                else:
                    out.write(out_frame)
                
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
            self.finished.emit(f"Processing complete! Saved to {output_path}")

    def stop(self):
        self.is_running = False
        self.mutex.lock()
        self.wait_cond.wakeAll()
        self.mutex.unlock()
