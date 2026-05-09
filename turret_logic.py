# turret_logic.py
import time
from adafruit_servokit import ServoKit

# --- Hardware Setup ---
kit = ServoKit(channels=16)

# State Variables
pan_angle, tilt_angle = 90.0, 90.0
pan_vel, tilt_vel = 0.0, 0.0
fire_angle = 90.0
running = True

# Physics Constants
ACC = 0.3
FRC = 0.90
TIME_LOOP = 0.02

# Keyboard State
keys = {"w": False, "s": False, "a": False, "d": False}

def calibrate():
    global pan_angle, tilt_angle
    pan_angle, tilt_angle = 90.0, 90.0
    
    kit.servo[0].angle = pan_angle
    print("Pan servo calibrated to 90 degrees.")
    time.sleep(1.0)
    
    kit.servo[1].angle = tilt_angle
    print("Tilt servo calibrated to 90 degrees.")
    time.sleep(1.0)
    
    kit.servo[2].angle = fire_angle
    print("Fire servo calibrated to 90 degrees.")
    time.sleep(1.0)

def smooth_reset():
    global pan_angle, tilt_angle, pan_vel, tilt_vel, running
    running = False
    print("Physics loop set to Unactive.")
    
    target = 90.0
    
    while abs(target - pan_angle) > 0.1 or abs(pan_vel) > 0.01 or \
          abs(target - tilt_angle) > 0.1 or abs(tilt_vel) > 0.01:
        
        pan_vel += (target - pan_angle) * 0.04
        tilt_vel += (target - tilt_angle) * 0.04
        
        pan_vel *= FRC
        tilt_vel *= FRC
        
        pan_angle += pan_vel
        tilt_angle += tilt_vel
        
        kit.servo[0].angle = max(0, min(180, pan_angle))
        kit.servo[1].angle = max(0, min(180, tilt_angle))
        time.sleep(TIME_LOOP)

    kit.servo[0].angle = 90
    kit.servo[1].angle = 90

def physics_loop():
    global pan_angle, tilt_angle, pan_vel, tilt_vel
    
    while running:
        if keys["w"]: tilt_vel += ACC
        if keys["s"]: tilt_vel -= ACC
        if keys["a"]: pan_vel += ACC
        if keys["d"]: pan_vel -= ACC
        
        pan_vel *= FRC
        tilt_vel *= FRC
        
        pan_angle += pan_vel
        tilt_angle += tilt_vel
        
        pan_angle = max(0, min(180, pan_angle))
        tilt_angle = max(0, min(180, tilt_angle))
        
        kit.servo[0].angle = pan_angle
        kit.servo[1].angle = tilt_angle
        time.sleep(TIME_LOOP)