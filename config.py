# config.py
# Physical wiring + tuned constants for the turret. Single source of truth,
# imported by turret/logic.py, turret/vision.py, tools/color_tracker.py, and
# tools/vision_test.py — see docs/NOTES.md ("v1.1") for why this file exists.

# --- Servo wiring (PCA9685 channels) ---
PAN_CHANNEL = 0
TILT_CHANNEL = 1
FIRE_CHANNEL = 2

# --- Physics loop ---
ACC = 0.3
FRC = 0.90
TIME_LOOP = 0.02
SERVO_EPS = 0.05

# --- Fire sequence (fire servo sweeps FIRE_MIN -> FIRE_MAX and snaps back) ---
FIRE_MIN = 90.0
FIRE_MAX = 150.0
FIRE_STEP = 5.0
FIRE_HOLD_SECONDS = 0.1
FIRE_HOLD_TICKS = max(1, round(FIRE_HOLD_SECONDS / TIME_LOOP))

# --- Autonomous tracking (v2.0 scaffold — unused until vision is wired in) ---
KP = 0.0

# --- Vision ---
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480
DEFAULT_FPS = 60      # turret_vision.py's own default, used by vision_test.py's raw feed test
TRACKING_FPS = 30     # color_tracker.py asks for less: it does per-frame CV work, not just display
