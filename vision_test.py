import cv2
import time
from turret_vision import TurretVision

def main():
    # 1. Initialize our vision class at 640x480 for speed
    vision = TurretVision(width=640, height=480, fps=60)
    
    print("Starting Live Feed... Press 'q' in the window to quit.")
    
    # Give the background thread a moment to grab the first few frames
    time.sleep(1.0) 

    try:
        while True:
            # 2. Grab the latest frame from the "desk" (shared memory)
            frame = vision.get_frame()
            
            if frame is not None:
                # 3. Swap colors: Camera (RGB) -> OpenCV (BGR)
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # 4. Draw a simple crosshair (for your turret testing!)
                cv2.drawMarker(bgr_frame, (200, 290), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
                
                # 5. Display the window
                cv2.imshow("Turret Eye - 60 FPS", bgr_frame)
            
            # Use waitKey(1) to keep the window alive and check for 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping vision test...")
    finally:
        # 6. Clean up: Release the camera and close windows
        vision.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()