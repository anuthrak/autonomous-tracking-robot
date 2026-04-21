# Autonomous Tracking Robot
Autonomous tracking pan-tilt robot using Raspberry Pi and utilizes the keyboard &amp; computer vision for inputs.

## Hardware Set-up

### 1. Raspberry Pi 
This project is designed to run "headless," controlled remotely via VNC (Virtual Network Computing). Follow these steps to access the Raspberry Pi desktop from your primary computer:

1. Identify the Raspberry Pi IP Address
Open your computer's terminal and ping the device's hostname to resolve its local IP address:

```bash
ping [raspberry-pi-name].local
```

- NOTE: The default hostname is usually raspberrypi. If successful, the terminal will display the IP address (e.g., 192.168.1.XX).

2. Connect via VNC Viewer

- Download: Install RealVNC Viewer on your workstation.

- Connect: Open the application and enter the IP address found in the previous step.
- Authenticate: Enter your Raspberry Pi credentials (default user is pi) to view the desktop interface.

### 2. Pan-tilt & Motion
The mechanical movement is handled by a dual-axis system, providing a wide field of regard for tracking targets.

#### Servos
This system utilizes two high-torque servo motors to achieve 2D movement (Pan/Tilt). With both axes capable of $180^\circ$ rotation, the system achieves a total coverage area of a full hemisphere.

This pan-tilt system uses 2 servo motors for 2-dimensional movement (left-right, up-down), totaling a full hemisphere coverage.  

#### Servo Driver (PCA9685)
To ensure stable power delivery and precise PWM (Pulse Width Modulation) control, we use the PCA9685 16-Channel 12-bit Driver.

### 3. Hardware Wiring & Power Management

[!CAUTION]
Power Safety: Never attempt to power the servo motors directly from the Raspberry Pi’s 5V pins. This can cause significant voltage drops (brownouts) or permanent damage to the Pi. Always use an external power source for the motors.

#### 1. PCA9685 to Raspberry Pi (Logic & Data)
The driver communicates with the Pi via the I2C protocol. Connect the pins on the side of the driver board to the Pi's GPIO header as follows:

- GPIO 1 (3.3V) -> VCC

- GPIO 2 (SDA) -> SDA
- GPIO 3 (SCL) -> SCL
- GROUND -> GROUND

Connect the PCA9685 to an external power source (5V +) for stability and workflow organization. 

#### 2. Servos to PCA9685
The PCA9685 features 16 rows of 3-pin headers. Each row is color-coded on many boards to help with orientation (typically Black/GND, Red/V+, and Yellow or White/PWM).

- Pan Axis -> Channel 0

- Tilt Axis -> Channel 1

## Software Set-up

