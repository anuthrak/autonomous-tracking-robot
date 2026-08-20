import cv2
import numpy as np
import time
from turret_vision import TurretVision

def _nothing(x):
    pass

def main():
    width, height = 640, 480
    vision = TurretVision(width=width, height=height, fps=30)
    center = (width // 2, height // 2)

    cv2.namedWindow("Controls")
    cv2.createTrackbar("H Min", "Controls", 0, 179, _nothing)
    cv2.createTrackbar("H Max", "Controls", 179, 179, _nothing)
    cv2.createTrackbar("S Min", "Controls", 0, 255, _nothing)
    cv2.createTrackbar("S Max", "Controls", 255, 255, _nothing)
    cv2.createTrackbar("V Min", "Controls", 0, 255, _nothing)
    cv2.createTrackbar("V Max", "Controls", 255, 255, _nothing)
    # A window with only trackbars and no image ever shown in it can render
    # blank/collapsed on some OpenCV GUI backends. Showing a dummy image
    # forces it to actually draw.
    cv2.imshow("Controls", np.zeros((1, 400), np.uint8))

    print("Tune the trackbars until only your target object is white in the Mask window.")
    print("Press 'p' to print the current HSV range, 'q' to quit.")

    time.sleep(1.0)

    try:
        while True:
            frame = vision.get_frame()
            if frame is None:
                continue

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower = (
                cv2.getTrackbarPos("H Min", "Controls"),
                cv2.getTrackbarPos("S Min", "Controls"),
                cv2.getTrackbarPos("V Min", "Controls"),
            )
            upper = (
                cv2.getTrackbarPos("H Max", "Controls"),
                cv2.getTrackbarPos("S Max", "Controls"),
                cv2.getTrackbarPos("V Max", "Controls"),
            )

            mask = cv2.inRange(hsv, lower, upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            display = frame.copy()
            cv2.drawMarker(display, center, (0, 255, 0), cv2.MARKER_CROSS, 20, 2)

            if contours:
                largest = max(contours, key=cv2.contourArea)
                (x, y), radius = cv2.minEnclosingCircle(largest)
                # Ignore small noise blobs so a stray pixel or two doesn't
                # register as a detection.
                if radius > 8:
                    cx, cy = int(x), int(y)
                    cv2.circle(display, (cx, cy), int(radius), (0, 0, 255), 2)
                    cv2.circle(display, (cx, cy), 4, (0, 0, 255), -1)
                    cv2.line(display, center, (cx, cy), (255, 0, 0), 1)
                    dx, dy = cx - center[0], cy - center[1]
                    cv2.putText(display, f"dx={dx} dy={dy}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Turret Eye", display)
            cv2.imshow("Mask", mask)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                print(f"HSV range -> lower={lower}, upper={upper}")

    except KeyboardInterrupt:
        print("\nStopping color tracker...")
    finally:
        vision.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
