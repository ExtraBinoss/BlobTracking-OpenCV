import cv2
import numpy as np
from collections import OrderedDict

class CentroidTracker:
    def __init__(self, max_disappeared=50):
        self.next_object_id = 0
        self.objects = OrderedDict() # Stores (centroid_x, centroid_y, radius)
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared

    def register(self, centroid, radius):
        self.objects[self.next_object_id] = (centroid[0], centroid[1], radius)
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        # Process input rects into centroids and radii
        input_centroids = np.zeros((len(rects), 2), dtype="int")
        input_radii = np.zeros(len(rects), dtype="int")
        
        for (i, (start_x, start_y, end_x, end_y)) in enumerate(rects):
            cX = int((start_x + end_x) / 2.0)
            cY = int((start_y + end_y) / 2.0)
            input_centroids[i] = (cX, cY)
            # Use max dimension for radius approximation
            w = end_x - start_x
            h = end_y - start_y
            input_radii[i] = int(max(w, h) / 2.0)

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i], input_radii[i])
        else:
            object_ids = list(self.objects.keys())
            # Extract just centroids for distance calculation
            object_centroids = [o[:2] for o in self.objects.values()]

            D = np.linalg.norm(np.array(object_centroids) - input_centroids[:, np.newaxis], axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[col]
                # Update with new centroid AND new radius
                self.objects[object_id] = (input_centroids[row][0], input_centroids[row][1], input_radii[row])
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            if D.shape[0] >= D.shape[1]:
                for row in unused_rows:
                    self.register(input_centroids[row], input_radii[row])
            else:
                for col in unused_cols:
                    object_id = object_ids[col]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)

        return self.objects

class BlobDetector:
    def __init__(self):
        self.min_area = 100
        self.max_area = 100000
        self.dilation = 0
        self.blur = 0
        self.threshold = 127
        self.mode = "grayscale" # grayscale, edges, color
        
        # Edge Detection (Canny) params
        self.canny_low = 50
        self.canny_high = 150
        
        # Color Isolation (HSV) params
        self.h_min = 0
        self.s_min = 0
        self.v_min = 0
        self.h_max = 179
        self.s_max = 255
        self.v_max = 255

    def update_params(self, params):
        self.min_area = params.get("min_area", self.min_area)
        self.max_area = params.get("max_area", self.max_area)
        self.dilation = params.get("dilation", self.dilation)
        self.blur = params.get("blur", self.blur)
        self.threshold = params.get("threshold", self.threshold)
        self.mode = params.get("mode", self.mode)
        
        self.canny_low = params.get("canny_low", self.canny_low)
        self.canny_high = params.get("canny_high", self.canny_high)
        
        self.h_min = params.get("h_min", self.h_min)
        self.s_min = params.get("s_min", self.s_min)
        self.v_min = params.get("v_min", self.v_min)
        self.h_max = params.get("h_max", self.h_max)
        self.s_max = params.get("s_max", self.s_max)
        self.v_max = params.get("v_max", self.v_max)

    def detect(self, frame):
        # 1. Grayscale / Pre-processing
        if self.mode == "color":
            # For color mode, we work in HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower = np.array([self.h_min, self.s_min, self.v_min])
            upper = np.array([self.h_max, self.s_max, self.v_max])
            thresh = cv2.inRange(hsv, lower, upper)
        else:
            # Grayscale for standard and edges
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame

            # Blur (Grouping aid)
            k = 2 * self.blur + 1
            blurred = cv2.GaussianBlur(gray, (k, k), 0)

            if self.mode == "edges":
                # Canny Edge Detection
                thresh = cv2.Canny(blurred, self.canny_low, self.canny_high)
            else:
                # Standard Thresholding (Inverted)
                _, thresh = cv2.threshold(blurred, self.threshold, 255, cv2.THRESH_BINARY_INV)

        # 4. Dilate (Grouping: expanding white regions to merge them)
        if self.dilation > 0:
            kernel = np.ones((self.dilation, self.dilation), np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=1)

        # 5. Find Contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rects = []
        keypoints = [] 

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_area < area < self.max_area:
                # Bounding box
                x, y, w, h = cv2.boundingRect(cnt)
                rects.append((x, y, x+w, y+h))
                
                # Center
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = x + w//2, y + h//2
                
                keypoints.append(cv2.KeyPoint(float(cX), float(cY), 10.0))
             
        return rects, keypoints, thresh # Return thresh for debug/preview

