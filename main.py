# main.py
import os
import time
import threading
from sshkeyboard import listen_keyboard
import turret_logic as turret

# On_press function
def press(key):
    if key in turret.keys:
        turret.keys[key] = True

    # Firing mechanism (non-blocking: advanced by the physics loop
    # so this callback never stalls the keyboard listener thread)
    elif key == "f":
        turret.request_fire()

# On_release function
def release(key):
    if key in turret.keys:
        turret.keys[key] = False

# Start Keyboard Thread
threading.Thread(target=lambda: listen_keyboard(
    on_press=press, 
    on_release=release, 
    delay_second_char=0.001
), daemon=True).start()

# Wrap main function in try/catch for lifecycle management
try:
    print("============================")
    print("Initializing Turret...")
    turret.calibrate()
    print("Physics loop set to Active.")
    print("============================")
    print("\nTurret Online. WASD to move, F to fire, Ctrl+C to exit.")
    turret.physics_loop()

# Unknown Exceptions
except KeyboardInterrupt:
    print("\n============================")
    print("[USER] Shutting down...")
    time.sleep(1)
    turret.smooth_reset()
    time.sleep(1)

# Manual Shutdown by User via Ctrl+C
except Exception as e:
    print(f"\n[ERROR] Shutting down due to: {e}")
    time.sleep(1)
    turret.smooth_reset()
    time.sleep(1)

# Ensure terminal is clear of sshkeyboard
finally:
    os.system("stty echo")
    time.sleep(1)
    print("Safe shutdown complete.")
    time.sleep(1)
