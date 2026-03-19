# Logitech Gamepad F310 Support Guide

This project now includes full support for the Logitech Gamepad F310 controller for wireless/gamepad control of the automated platform.

## Installation

Before using the joystick support, install the required dependency:

```bash
pip install pygame
```

## Features

The Logitech Gamepad F310 provides the following control mappings:

### Axis Controls (Analog Sticks & D-Pad)

| Input | Action |
|-------|--------|
| **Left Stick Horizontal** | X-Axis Movement (Left/Right) |
| **Left Stick Vertical** | Y-Axis Movement (Up/Down) |
| **Right Stick Vertical** | Z-Axis Movement (Up/Down) |
| **D-Pad Horizontal** | Alternative X-Axis Control |
| **D-Pad Vertical** | Alternative Y-Axis Control |

### Button Controls

| Button | Action |
|--------|--------|
| **A Button** | Roll CW (Clockwise) |
| **Y Button** | Roll CCW (Counter-Clockwise) |
| **X Button** | Yaw CCW (Counter-Clockwise) |
| **B Button** | Yaw CW (Clockwise) |
| **LB (Left Bumper)** | Z-Axis Up |
| **RB (Right Bumper)** | Z-Axis Down |

### Trigger Controls

| Trigger | Action |
|---------|--------|
| **LT (Left Trigger)** | Roll CCW (Progressive) |
| **RT (Right Trigger)** | Roll CW (Progressive) |

## Usage

The joystick handler automatically:
- Detects connected controllers on startup
- Initializes the Logitech Gamepad F310 (or any connected gamepad if F310 not found)
- Displays connection status in the GUI's "Joystick Status" group
- Sends commands to the Arduino via serial communication

The joystick controls work **simultaneously** with the GUI buttons - you can use both at the same time.

## Technical Details

### Files Added/Modified

- **joystick_handler.py** - New module handling all joystick input and command translation
- **main.py** - Updated to initialize and integrate the joystick handler

### Deadzone

The joystick has a configurable deadzone of 0.3 (30%) to prevent drift and accidental inputs. Adjust in `joystick_handler.py` if needed:

```python
self.deadzone = 0.3  # Change this value (0.0-1.0)
```

### Threading

The joystick handler runs in a separate thread to avoid blocking the GUI. Status updates are thread-safe using PyQt5 signals.

## Troubleshooting

### Controller Not Detected

If your controller isn't detected:

1. Ensure pygame is installed: `pip install pygame`
2. Verify controller is connected to USB
3. Test with pygame's built-in controller detection
4. Check the "Joystick Status" label in the GUI - it shows connection status

### Commands Not Being Sent

- Verify serial port is correctly set in `main.py` (currently `COM6`)
- Check Arduino is receiving commands via the GUI buttons first
- Review console output for "Sent: XXX" messages

### Using Different Gamepad

The code automatically falls back to any connected gamepad if Logitech F310 isn't found. It looks for:
- "logitech" in device name
- "f310" in device name  
- "gamepad" in device name

If using a different gamepad, you may need to adjust button mappings in `joystick_handler.py`.

## Advanced Configuration

### Adjusting Sensitivity

Modify the deadzone threshold in `joystick_handler.py`:

```python
self.deadzone = 0.2  # More sensitive
self.deadzone = 0.4  # Less sensitive
```

### Custom Button Mappings

Edit the `handle_button_press()` method in `joystick_handler.py` to remap buttons:

```python
def handle_button_press(self, button):
    if button == self.BUTTON_Y:
        self.send_command("YOUR_COMMAND")
    # ... other buttons
```

### Custom Axis Mappings

Edit the `handle_axis_motion()` method to customize analog stick behavior.

## References

- Pygame Joystick Documentation: https://www.pygame.org/docs/ref/joystick.html
- Logitech F310 Controller Documentation
