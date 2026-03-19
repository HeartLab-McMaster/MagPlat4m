# MagPlat4m - Automated Magnetic Platform Control System

A comprehensive PyQt5-based GUI application for controlling an automated research platform with multi-axis motion capabilities and magnetic field measurement integration.

## Overview

MagPlat4m is a control system designed for the IBEHS 3H03 collaborative research project. It provides intuitive control of an automated platform via serial communication with Arduino hardware, supports joystick/gamepad input, and integrates real-time magnetic field measurements through a Teslameter device.

## Features

- **Multi-Axis Control**: X, Y, Z axis positioning and rotational control (Roll, Pitch, Yaw)
- **Joystick Support**: Full Logitech Gamepad F310 controller integration with button and analog stick mappings
- **Serial Communication**: Direct Arduino platform control with real-time feedback
- **Magnetic Field Mapping**: Integration with Lakeshore Teslameter for field measurements
- **Data Visualization**: 2D/3D field mapping and plotting capabilities
- **Data Export**: Generate and save field measurement data in CSV format
- **Real-time Monitoring**: Live status display and motion feedback

## Hardware Requirements

- **Microcontroller**: Arduino-compatible board (detailed in `Arduino/` directory)
- **Motion Platform**: 3-axis automated positioning system controlled via Arduino
- **Measurement Device**: Lakeshore Teslameter for magnetic field measurements
- **Optional**: Logitech Gamepad F310 controller for wireless platform control

## Installation

### Prerequisites

- Python 3.7 or higher
- USB serial connectivity to Arduino
- Optional: Connected Logitech Gamepad F310

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd MagPlat4m
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

The requirements include:
- **PyQt5** (>=5.15.0) - GUI framework
- **pyserial** (>=3.5) - Serial communication
- **numpy** (>=1.21.0) - Numerical computing
- **pandas** (>=1.3.0) - Data manipulation
- **matplotlib** (>=3.4.0) - Data visualization
- **scipy** (>=1.7.0) - Scientific computing
- **pygame** (>=2.1.0) - Joystick support
- **lakeshore** (>=3.0.0) - Teslameter integration

### Step 3: Arduino Setup

Refer to `JOYSTICK_SETUP.md` for detailed Joystick controller configuration and `Arduino/` directory for platform firmware installation.

## Usage

### Launching the Application

```bash
python main.py
```

The GUI will open with the following main components:
- **Serial Port Configuration**: Select and connect to Arduino device
- **Motion Controls**: Manual axis and rotation controls
- **Joystick Status**: Real-time connection and input status
- **Teslameter Interface**: Magnetic field measurement controls
- **Data Visualization**: Field mapping and analysis tools

### Joystick Control

For detailed joystick control mappings and setup instructions, see [JOYSTICK_SETUP.md](./JOYSTICK_SETUP.md).

**Quick Reference**:
- Left Stick: X/Y axis movement
- Right Stick: Z axis and rotation
- Buttons: Roll/Yaw control
- Triggers: Progressive rotation control

## Project Structure

```
MagPlat4m/
├── main.py                 # Main GUI application
├── utmas_ui.py            # UI components and layout
├── joystick_handler.py    # Joystick input handling
├── teslameter.py          # Teslameter measurement interface
├── Arduino/               # Hardware firmware
│   ├── platform/          # Platform-specific firmware
│   │   └── platform.ino   # Platform firmware implementation
│   └── path_following/    # Path following algorithms
│       └── path_following.ino
├── assets/                # Application assets
├── requirements.txt       # Python dependencies
├── JOYSTICK_SETUP.md     # Joystick configuration guide
└── README.md             # This file
```

## Configuration

### Serial Port
The application automatically detects available serial ports. Select the appropriate port for your Arduino device at startup.

### Teslameter Connection
Configure the Teslameter connection through the GUI's measurement interface. Ensure the device is powered and connected via USB before launching.

### Joystick
Joystick detection is automatic. Connect your gamepad before launching the application for automatic initialization.

## Data Output

The application generates field measurement data in the `results/` directory:
- CSV files with field measurement data
- Matplotlib visualizations of field maps
- 3D surface plots of magnetic field topology

## Development Notes

- **Authors**: Ryan Seyedan, Sonia Parekh, Veerash Palanichamy
- **Project Date**: Created April 2025, Updated March 2026

## Troubleshooting

### Serial Connection Issues
- Verify Arduino driver installation
- Check USB cable connection
- Ensure correct COM port is selected in GUI

### Joystick Not Detected
- Connect gamepad before launching application
- Verify pygame installation: `pip install pygame`
- Check device compatibility (supports Logitech Gamepad F310)

### Teslameter Connection Issues
- Verify USB connection and power
- Check Lakeshore driver installation
- Review Teslameter configuration in GUI