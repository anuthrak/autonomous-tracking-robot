import time
import threading
from sshkeyboard import listen_keyboard
from adafruit_servokit import ServoKit

# --- Setup ---
kit = ServoKit(channels=16)

# Initial Positions
pan_angle = 90.0
tilt_angle = 90.0
fire_angle = 90.0

# Initial Velocities
pan_vel = 0.0
tilt_vel = 0.0

# --- Constants (Adjust these to change the 'feel') ---
ACCEL = 0.4        # Speed added per loop while holding key
FRICTION = 0.88    # Speed retained per loop (0.95 = slidey, 0.80 = snappy)
MAX_SPEED = 3.0    # Speed limit per axis

# Track held keys
keys = {"w": False, "s": False, "a": False, "d": False}

def press(key):
    global keys
    if key in keys:
        keys[key] = True
    
    # Firing is a single action, so we trigger it on press
    if key == "f":
        fire()

def release(key):
    global keys
    if key in keys:
        keys[key] = False

def fire():
    print("FIRING!")
    # Quick strike for firing
    for a in range(90, 150, 10):
        kit.servo[4].angle = a
        time.sleep(0.01)
    time.sleep(0.05)
    kit.servo[4].angle = 90

def physics_loop():
    global pan_angle, tilt_angle, pan_vel, tilt_vel
    
    print("Turret Online. WASD to move, F to fire, Esc to quit.")
    
    while True:
        # 1. Acceleration
        if keys["w"]: tilt_vel -= ACCEL
        if keys["s"]: tilt_vel += ACCEL
        if keys["a"]: pan_vel += ACCEL
        if keys["d"]: pan_vel -= ACCEL

        # 2. Apply Friction (The Ease-Out)
        pan_vel *= FRICTION
        tilt_vel *= FRICTION

        # 3. Apply Velocity to Angle
        pan_angle += pan_vel
        tilt_angle += tilt_vel

        # 4. Stay in Bounds (0-180)
        pan_angle = max(0, min(180, pan_angle))
        tilt_angle = max(0, min(180, tilt_angle))

        # 5. Move Hardware
        kit.servo[0].angle = pan_angle
        kit.servo[1].angle = tilt_angle
        
        # 50Hz Update Rate
        time.sleep(0.02)

# Start keyboard listener thread
threading.Thread(target=lambda: listen_keyboard(on_press=press, on_release=release), daemon=True).start()

# Start the main physics engine
try:
    physics_loop()
except KeyboardInterrupt:
    print("\nShutting down...")