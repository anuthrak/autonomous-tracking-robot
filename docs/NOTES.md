# Project Notes & Learning Log

Personal reference for concepts used in this project and where they show up in
code. Versioned alongside the project itself — not the software version, but
a marker of "what stage of understanding/capability was this at."

**See also:**
- [Single Point of Control](https://claude.ai/code/artifact/4c28788d-6662-431b-bf55-73afa9a71b58)
  (also saved locally at `notes/single-point-of-control.html`) — diagrammed
  deep-dive on the v1.1 changes below (no owner for shared state, config
  scattered across files).
- [Signal & Servo](https://claude.ai/code/artifact/1e27b264-bda4-42a3-961e-be4ae7e82d5b)
  (also saved locally at `notes/project-map.html`) — illustrated map of the
  whole project: the physical rig, the module map, current control flow,
  concepts, and this same roadmap.

---

## Changelog

- **v1.1** — Structural cleanup, no new behavior yet:
  - Added `config.py` as the single source of truth for servo channels,
    physics/fire constants, and vision defaults. Every other file now
    imports from it instead of holding its own copy.
  - `turret_logic.py` gained a `mode` flag (`"MANUAL" | "AUTO"`) and a single
    arbiter, `_control_step()`, that is now the *only* code allowed to touch
    `pan_vel`/`tilt_vel`. Keyboard input goes through `set_key()`, vision
    input will go through `set_target_error()` — neither writes velocity
    directly anymore.
  - `main.py` calls `turret.set_key()` instead of mutating `turret.keys`
    directly, and gained an `m` key to toggle mode (currently a no-op in
    `AUTO` since `KP = 0` and nothing calls `set_target_error()` yet — that's
    v2.0).

---

## Roadmap

- **v1.x — Manual + Vision (separate)** — current stage. Turret drives by
  hand (WASD), vision detects a colored target, but the two don't talk yet.
  Bump the minor version (v1.1, v1.2, ...) for tuning/cleanup/small features
  within this stage — e.g. better HSV tuning workflow, refining physics
  constants, adding a search/idle animation.
- **v2.0 — Closed loop (autonomous tracking)** — vision's `dx, dy` error
  feeds into the turret's control loop and actually drives the servos.
  Manual control becomes an override mode, not the only mode.
- **v3.0 — Instrumentation & metrics** — logging, graphs, tuning
  methodology. This is what turns the project from "it works" into
  something with data behind it (and what makes the resume version of this
  project credible).

See below for what v2 and v3 concretely might include.

---

## v1.0 — Concepts in use right now

### Control / physics (`turret_logic.py`)
- **Euler integration of motion**: each tick, `velocity += acceleration`,
  then `position += velocity`. This is the same discrete-time integration
  used in basically all real-time simulation and robotics control loops.
- **Friction/damping (`FRC = 0.90`)**: velocity is multiplied by a
  <1 factor every tick, so it decays toward zero instead of coasting
  forever. Without this, holding a key would accelerate the turret
  indefinitely. This is what makes the motion feel smooth instead of
  jerky/instant.
- **Clamping**: `pan_angle = max(0, min(180, pan_angle))` — keeps the
  physics simulation from commanding a servo angle outside its physical
  range.
- **State machine**: the fire sequence (`fire_state`:
  `idle → extending → holding → retracting`) is a small explicit state
  machine advanced one step per tick, rather than a blocking
  sleep-based sequence. This is *why* firing doesn't freeze the rest of
  the robot.
- **Non-blocking I/O pattern**: `request_fire()` only flips a flag; the
  actual servo movement happens later in `physics_loop()`. Keeps the
  keyboard callback thread fast so it never misses a keypress.
- **Hardware abstraction / mock pattern**: `try: import ServoKit / except:
  use _MockServoKit`. This lets the exact same control code run on real
  hardware or in simulation on a laptop, which is why we can develop and
  test the physics without a Pi attached.
- **Dirty-checking before I/O** (`_write_servo`): only writes to the servo
  over I2C if the angle changed more than `SERVO_EPS`. I2C writes are slow
  relative to a 50Hz loop; skipping redundant writes keeps the bus free.
- **Single source of truth (`config.py`, added v1.1)**: servo channels,
  physics constants, and vision defaults live in exactly one place now.
  Fixes a real bug-in-waiting: `color_tracker.py` and `vision_test.py` had
  silently disagreed on camera FPS (30 vs 60) with no config file to make
  that visible.
- **Arbiter / mediator pattern (`_control_step()`, added v1.1)**: rather
  than letting keyboard input and (eventually) vision both write
  `pan_vel`/`tilt_vel` directly, both submit a *request* (`set_key()`,
  `set_target_error()`) and one function, gated on `mode`, is the only
  place that actually assigns velocity. This is what stops two input
  sources from racing each other in the same tick once vision joins in
  v2.0.

### Concurrency (`main.py`, `turret_vision.py`)
- **Daemon threads**: the keyboard listener and camera capture both run on
  `daemon=True` threads, so they don't prevent the program from exiting
  when the main thread ends.
- **Producer/consumer with a lock**: `TurretVision._update()` (producer)
  writes the latest camera frame; `get_frame()` (consumer) reads it. A
  `threading.Lock` prevents the two from touching `self.frame` at the same
  moment and tearing the data.
- **Lifecycle management**: `try / except KeyboardInterrupt / except
  Exception / finally` in `main.py` ensures the turret always eases back to
  center (`smooth_reset()`) and the terminal is restored, however the
  program exits.

### Vision (`turret_vision.py`, `color_tracker.py`, `vision_test.py`)
- **HSV color space thresholding**: converting BGR → HSV before
  thresholding, because HSV separates *color* (hue) from *brightness*
  (value), making detection much more robust to lighting changes than
  thresholding raw RGB.
- **Morphological operations (erode/dilate)**: cleans up a noisy binary
  mask — erode removes small stray white pixels, dilate restores the size
  of the real blob that's left.
- **Contour detection**: `cv2.findContours` + picking the largest by area
  is the simplest possible way to pick "the one object we care about" out
  of a noisy mask.
- **Radius/size thresholding**: ignoring detections below a minimum radius
  filters out single-pixel noise that survives the morphology step.
- **Interactive tuning via trackbars**: `color_tracker.py`'s HSV sliders
  exist because the right threshold values are lighting/camera-dependent
  and need to be found empirically, not hardcoded.

---

## v2.0 (proposed) — Closing the loop

This is the "vision drives the turret" milestone. Rough shape of what it'll
need, as a preview before we build it:

- **Proportional control**: turn pixel error into a servo command, e.g.
  `pan_vel += Kp * dx`. This is the simplest possible feedback controller —
  push the turret toward the target proportional to how far off it is.
  The plumbing for this already exists as of v1.1 (`_control_step()`'s
  `AUTO` branch, `config.KP`) — what's left is an actual tracking loop that
  calls `set_target_error(dx, dy)` with real vision data, and tuning `KP`
  away from its placeholder `0`.
- **Shared state between threads, take two**: `target_dx`/`target_dy` are
  plain globals as of v1.1, safe for now because nothing writes them
  concurrently yet. Once a tracking loop actually calls
  `set_target_error()` from a thread running alongside `physics_loop()`,
  this needs the same lock-protected pattern as `TurretVision.frame`.
- **Mode switching**: done in v1.1 — `mode` flag plus the `m` key toggle
  already exist. What's missing is a reason to be in `AUTO`: real vision
  data feeding it.
- **Target-loss handling**: what happens when the color tracker sees
  nothing for N frames? Hold position? Re-center? This needs a deliberate
  answer, not just "do nothing."
- **Tuning by feel first**: expect P-only control to either lag (Kp too
  low) or oscillate/overshoot (Kp too high). We'll tune `Kp` on hardware by
  eye before deciding whether PID (adding `Ki` for steady-state error,
  `Kd` for damping oscillation) is actually needed — no point adding
  complexity the system doesn't need.
- **Loop-rate mismatch**: the physics loop runs at 50Hz; the vision
  pipeline may run slower. The tracking loop needs to tolerate reading a
  "stale" target error between camera frames without instability.

## v3.0 (proposed) — Instrumentation & metrics

Only meaningful once v2 exists — you can't measure a loop that isn't
closed yet.

- **Structured logging**: log per-tick `(timestamp, dx, dy, pan_angle,
  tilt_angle, loop_dt)` to CSV from the control loop itself.
- **Decoupled analysis**: a separate `analyze.py` (pandas/matplotlib) reads
  the logs and produces plots — kept out of the real-time loop so
  plotting never risks slowing down control.
- **Classic control-systems metrics**: step response, settling time,
  overshoot %, rise time — move a target suddenly and measure how the
  turret converges. These are the standard vocabulary for describing
  *any* feedback controller's performance, not specific to this project.
- **Loop timing/jitter**: histogram of actual tick duration vs. the
  target `TIME_LOOP`, to check the control loop is running consistently.
- **Vision pipeline FPS**: measured frame rate of the camera thread vs.
  requested `fps`.
- **Lock-acquisition rate**: over N trials, what fraction of the time does
  the turret successfully find and lock onto the target?
- **README payoff**: this is the stage that produces the graphs/numbers
  worth putting in a portfolio write-up or resume bullet.

Later ideas (v3.1+, not scoped yet): predictive tracking (estimating
target velocity to reduce lag), search behavior when target is lost,
multi-target handling.
