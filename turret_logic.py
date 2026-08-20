# turret_logic.py
import time

# --- Hardware Setup ---
# On real Raspberry Pi hardware this binds to the PCA9685 over I2C. Off-Pi
# (e.g. developing on a laptop) the import/instantiation raises before we
# ever get here, so fall back to an in-memory mock that just records the
# angle it was told to move to. Keeps the control logic importable/runnable
# for testing without hardware attached.
try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
except Exception as e:
    print(f"[WARN] ServoKit hardware unavailable ({e}); running in SIMULATION mode.")

    class _MockServo:
        def __init__(self, channel):
            self.channel = channel
            self.angle = None

    class _MockServoKit:
        def __init__(self, channels=16):
            self.servo = [_MockServo(i) for i in range(channels)]

    kit = _MockServoKit(channels=16)

# State Variables
pan_angle, tilt_angle = 90.0, 90.0
pan_vel, tilt_vel = 0.0, 0.0
running = True

# Physics Constants
ACC = 0.3
FRC = 0.90
TIME_LOOP = 0.02

# Fire Constants (fire servo sweeps 90 -> 150 and snaps back)
FIRE_MIN = 90.0
FIRE_MAX = 150.0
FIRE_STEP = 5.0
FIRE_HOLD_TICKS = max(1, round(0.1 / TIME_LOOP))

# Keyboard State
keys = {"w": False, "s": False, "a": False, "d": False}

# Fire State Machine ("idle" | "extending" | "holding" | "retracting")
fire_angle = FIRE_MIN
fire_state = "idle"
fire_hold_counter = 0

# Last angle actually written to each servo channel, so the physics/fire
# loops (running at 50Hz) only hit the I2C bus when the angle meaningfully
# changed instead of every tick regardless of movement.
SERVO_EPS = 0.05
_last_angles = [None, None, None]

def _write_servo(channel, angle):
    global _last_angles
    last = _last_angles[channel]
    if last is None or abs(angle - last) >= SERVO_EPS:
        kit.servo[channel].angle = angle
        _last_angles[channel] = angle

def calibrate():
    global pan_angle, tilt_angle, pan_vel, tilt_vel, fire_angle, fire_state, fire_hold_counter
    pan_angle, tilt_angle = 90.0, 90.0
    pan_vel, tilt_vel = 0.0, 0.0
    fire_angle = FIRE_MIN
    fire_state = "idle"
    fire_hold_counter = 0

    _write_servo(0, pan_angle)
    print("Pan servo calibrated to 90 degrees.")
    time.sleep(1.0)

    _write_servo(1, tilt_angle)
    print("Tilt servo calibrated to 90 degrees.")
    time.sleep(1.0)

    _write_servo(2, fire_angle)
    print("Fire servo calibrated to 90 degrees.")
    time.sleep(1.0)

def request_fire():
    """Non-blocking: called from the keyboard thread, arms the fire
    sequence for physics_loop() to advance. Ignored if already firing so
    holding 'f' can't stack sweeps."""
    global fire_state, fire_hold_counter
    if fire_state == "idle":
        fire_state = "extending"
        fire_hold_counter = 0

def _update_fire():
    global fire_angle, fire_state, fire_hold_counter

    if fire_state == "extending":
        fire_angle = min(FIRE_MAX, fire_angle + FIRE_STEP)
        _write_servo(2, fire_angle)
        if fire_angle >= FIRE_MAX:
            fire_state = "holding"

    elif fire_state == "holding":
        fire_hold_counter += 1
        if fire_hold_counter >= FIRE_HOLD_TICKS:
            fire_state = "retracting"

    elif fire_state == "retracting":
        fire_angle = FIRE_MIN
        _write_servo(2, fire_angle)
        fire_state = "idle"

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

        _write_servo(0, max(0, min(180, pan_angle)))
        _write_servo(1, max(0, min(180, tilt_angle)))
        time.sleep(TIME_LOOP)

    _write_servo(0, 90)
    _write_servo(1, 90)

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

        _write_servo(0, pan_angle)
        _write_servo(1, tilt_angle)

        _update_fire()

        time.sleep(TIME_LOOP)
