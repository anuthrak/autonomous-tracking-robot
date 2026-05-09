# Turret Vision

# Imports
import cv2
import threading
import time
from picamera2 import Picamera2

class TurretVision:
    def __init__(self, width=640, height=480, fps=60):
        self.picam2 = Picamera2()
        
        self.config = self.picam2.create_preview_configuration(
            main={"format": 'RGB888', "size": (width, height)},
            controls={"FrameRate": fps}
        )
        
        self.picam2.configure(self.config)
        self.picam2.start()
        
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        
    def _update(self):
        while self.running:
            # Capture frame into a numpy array
            new_frame = self.picam2.capture_array()
                
            with self.lock:
                self.frame = new_frame

    def get_frame(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        self.picam2.stop()
        
    
