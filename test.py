import os
import time
import threading
from sshkeyboard import listen_keyboard
from adafruit_servokit import ServoKit

# --- Setup ---
kit = ServoKit(channels=16)

# Initial Positions
pan_angle, tilt_angle = 90.0, 90.0
pan_vel, tilt_vel = 0.0, 0.0


fire_angle = 90.0

# Turret Feel
running = True
ACC = 0.3
FRC = 0.90
TIME_LOOP = 0.02

# Keys dictionary
keys = {"w": False, "s": False, "a": False, "d": False}

# FUNCTIONS
def calibrate():
    global pan_angle, tilt_angle
    
    kit.servo[0].angle = pan_angle
    print("Pan servo calibrated to 90 degrees.")
    time.sleep(1.5)

    kit.servo[1].angle = tilt_angle
    print("Tilt servo calibrated to 90 degrees.")
    time.sleep(1.5)

    kit.servo[2].angle = fire_angle
    print("Fire servo calibrated to 90 degrees.")
    time.sleep(1.5)

# Initializing Turret Message
print("============================")
print("Turret starting... (TEST MODE)")
time.sleep(1)

calibrate()

def press(key):
    global keys
    if key in keys:
        keys[key] = True
    elif key == "f":
        for a in range(90, 151, 5): 
            kit.servo[2].angle = a
            time.sleep(0.01)

        # Brief pause at the peak strike point
        time.sleep(0.1)

        # Snap back to ready position immediately
        kit.servo[2].angle = 90
        
def release(key):
    global keys
    if key in keys:
        keys[key] = False

def physics_loop():
    global pan_angle, tilt_angle, pan_vel, tilt_vel, running, ACC, FRC, TIME_LOOP
    
    while running:
        if keys["w"]: tilt_vel += ACC
        if keys["s"]: tilt_vel -= ACC
        if keys["a"]: pan_vel += ACC
        if keys["d"]: pan_vel -= ACC
        
        pan_vel *= FRC
        tilt_vel *= FRC
        
        if abs(pan_vel) < 0.01: pan_vel = 0.0
        if abs(tilt_vel) < 0.01: tilt_vel = 0.0
        
        pan_angle += pan_vel
        tilt_angle += tilt_vel
        
        pan_angle = max(0, min(180, pan_angle))
        tilt_angle = max(0, min(180, tilt_angle))
        
        kit.servo[0].angle = pan_angle
        kit.servo[1].angle = tilt_angle
        
        time.sleep(TIME_LOOP)
        
threading.Thread(target=lambda:
                 listen_keyboard(
                     on_press=press,
                     on_release=release,
                     delay_second_char=0.001
                     ),daemon=True).start()

try:
    print("Physics loop set to Active.")
    time.sleep(1.5)
    print("============================")
    print("Turret fully online. Press WASD for movement. Crtl + C to exit.")
    time.sleep(1.5)
    print("============================")
    physics_loop()
    
except Exception as e:
    print("Shutting down due to: {e}")
    running = False
    
except KeyboardInterrupt:
    print("User shutting down...")
    running = False
    calibrate()
    time.sleep(1.5)
    
finally:
    print("Turret has gone offline.")
    print("============================")
    os.system("stty echo")

        
        