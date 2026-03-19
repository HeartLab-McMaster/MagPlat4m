"""
Logitech Gamepad F310 Controller Handler
Provides joystick input support for the automated platform control
"""

import pygame
from pygame.locals import *
from PyQt5.QtCore import QThread, pyqtSignal
import threading
import time


class JoystickHandler(QThread):
    """
    Handles Logitech Gamepad F310 input and translates to platform commands
    """
    
    # Define signals for command sending
    send_command = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    # Logitech F310 Button/Axis Mapping
    # Buttons
    BUTTON_A = 0
    BUTTON_B = 1
    BUTTON_X = 2
    BUTTON_Y = 3
    BUTTON_LB = 4  # Left Bumper
    BUTTON_RB = 5  # Right Bumper
    BUTTON_BACK = 6
    BUTTON_START = 7
    BUTTON_LSTICK = 8  # Left Stick Press
    BUTTON_RSTICK = 9  # Right Stick Press
    
    # Axes
    AXIS_LX = 0  # Left Stick X
    AXIS_LY = 1  # Left Stick Y
    AXIS_RX = 2  # Right Stick X
    AXIS_RY = 3  # Right Stick Y
    AXIS_LT = 4  # Left Trigger (LT)
    AXIS_RT = 5  # Right Trigger (RT)
    AXIS_DPAD_X = 6  # D-Pad X
    AXIS_DPAD_Y = 7  # D-Pad Y
    
    def __init__(self, send_command_callback=None):
        super().__init__()
        self.running = False
        self.joystick = None
        self.send_command_callback = send_command_callback
        self.daemon = True
        
        # State tracking for continuous movement
        self.active_movements = set()
        self.deadzone = 0.3  # Joystick deadzone threshold
        self.dpad_state = {'x': 0, 'y': 0}  # Track dpad state
        
        # Initialize pygame
        try:
            pygame.init()
            pygame.joystick.init()
        except Exception as e:
            print(f"Failed to initialize pygame: {e}")
    
    def set_send_command_callback(self, callback):
        """Set the callback function for sending commands"""
        self.send_command_callback = callback
    
    def find_logitech_gamepad(self):
        """Find and initialize Logitech Gamepad F310"""
        joystick_count = pygame.joystick.get_count()
        
        if joystick_count == 0:
            self.status_changed.emit("No joysticks found")
            return False
        
        for i in range(joystick_count):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            name = joy.get_name().lower()
            
            # Check for Logitech controller
            if "logitech" in name or "f310" in name or "gamepad" in name:
                self.joystick = joy
                self.status_changed.emit(f"Connected: {joy.get_name()}")
                print(f"Logitech Gamepad F310 found: {joy.get_name()}")
                print(f"Buttons: {joy.get_numbuttons()}")
                print(f"Axes: {joy.get_numaxes()}")
                print(f"Hats: {joy.get_numhats()}")
                return True
        
        # If no Logitech found, use first available joystick
        if joystick_count > 0:
            joy = pygame.joystick.Joystick(0)
            joy.init()
            self.joystick = joy
            self.status_changed.emit(f"Using fallback joystick: {joy.get_name()}")
            print(f"Logitech not found, using: {joy.get_name()}")
            return True
        
        return False
    
    def send_command(self, command):
        """Send command via callback or signal"""
        if self.send_command_callback:
            self.send_command_callback(command)
        else:
            self.send_command.emit(command)
    
    def stop_movement(self, axis):
        """Stop movement for a given axis"""
        if axis == "X":
            self.send_command("XS")
            self.active_movements.discard("X")
        elif axis == "Y":
            self.send_command("YS")
            self.active_movements.discard("Y")
        elif axis == "Z":
            self.send_command("ZS")
            self.active_movements.discard("Z")
    
    def handle_axis_motion(self, axis, value):
        """Handle continuous analog stick/trigger movement"""
        
        # Left stick X: X-Axis (left/right movement)
        if axis == self.AXIS_LX:
            if abs(value) > self.deadzone:
                if value < -self.deadzone and "X" not in self.active_movements:
                    self.send_command("X-")
                    self.active_movements.add("X")
                elif value > self.deadzone and "X" not in self.active_movements:
                    self.send_command("X+")
                    self.active_movements.add("X")
            else:
                self.stop_movement("X")
        
        # Left stick Y: Y-Axis (up/down movement)
        elif axis == self.AXIS_LY:
            if abs(value) > self.deadzone:
                # Inverted Y-axis (typical joystick behavior)
                if value < -self.deadzone and "Y" not in self.active_movements:
                    self.send_command("Y+")
                    self.active_movements.add("Y")
                elif value > self.deadzone and "Y" not in self.active_movements:
                    self.send_command("Y-")
                    self.active_movements.add("Y")
            else:
                self.stop_movement("Y")
        
        # Right stick Y: Z-Axis (up/down movement)
        elif axis == self.AXIS_RY:
            if abs(value) > self.deadzone:
                # Inverted Y-axis
                if value < -self.deadzone and "Z" not in self.active_movements:
                    self.send_command("Z+")
                    self.active_movements.add("Z")
                elif value > self.deadzone and "Z" not in self.active_movements:
                    self.send_command("Z-")
                    self.active_movements.add("Z")
            else:
                self.stop_movement("Z")
        
        # D-Pad X: Alternative X-Axis control
        elif axis == self.AXIS_DPAD_X:
            if abs(value) > self.deadzone:
                if value < -self.deadzone and "X" not in self.active_movements:
                    self.send_command("X-")
                    self.active_movements.add("X")
                elif value > self.deadzone and "X" not in self.active_movements:
                    self.send_command("X+")
                    self.active_movements.add("X")
            else:
                self.stop_movement("X")
        
        # D-Pad Y: Alternative Y-Axis control
        elif axis == self.AXIS_DPAD_Y:
            if abs(value) > self.deadzone:
                if value < -self.deadzone and "Y" not in self.active_movements:
                    self.send_command("Y-")
                    self.active_movements.add("Y")
                elif value > self.deadzone and "Y" not in self.active_movements:
                    self.send_command("Y+")
                    self.active_movements.add("Y")
            else:
                self.stop_movement("Y")
        
        # Left Trigger: Roll control
        elif axis == self.AXIS_LT:
            if value > self.deadzone:
                self.send_command("R-")  # Roll CCW
            else:
                self.send_command("RS")  # Stop Roll
        
        # Right Trigger: Roll control (opposite)
        elif axis == self.AXIS_RT:
            if value > self.deadzone:
                self.send_command("R+")  # Roll CW
            else:
                self.send_command("RS")  # Stop Roll
    
    def handle_button_press(self, button):
        """Handle button press events"""
        
        # Y button: Roll CCW
        if button == self.BUTTON_Y:
            self.send_command("R-")
        # A button: Roll CW
        elif button == self.BUTTON_A:
            self.send_command("R+")
        # X button: Yaw CCW
        elif button == self.BUTTON_X:
            self.send_command("W-")
        # B button: Yaw CW
        elif button == self.BUTTON_B:
            self.send_command("W+")
        # LB button: Z Up
        elif button == self.BUTTON_LB:
            self.send_command("Z+")
        # RB button: Z Down
        elif button == self.BUTTON_RB:
            self.send_command("Z-")
        # Start button
        elif button == self.BUTTON_START:
            print("Start button pressed")
        # Back button
        elif button == self.BUTTON_BACK:
            print("Back button pressed")
    
    def handle_button_release(self, button):
        """Handle button release events"""
        
        # Stop roll/yaw on button release
        if button in [self.BUTTON_Y, self.BUTTON_A]:
            self.send_command("RS")
        elif button in [self.BUTTON_X, self.BUTTON_B]:
            self.send_command("WS")
        elif button in [self.BUTTON_LB, self.BUTTON_RB]:
            self.send_command("ZS")
    
    def run(self):
        """Main joystick input loop"""
        if not self.find_logitech_gamepad():
            self.status_changed.emit("Could not initialize joystick")
            return
        
        self.running = True
        clock = pygame.time.Clock()
        
        try:
            while self.running:
                # Process pygame events
                for event in pygame.event.get():
                    if event.type == pygame.JOYAXISMOTION:
                        self.handle_axis_motion(event.axis, event.value)
                    
                    elif event.type == pygame.JOYBUTTONDOWN:
                        self.handle_button_press(event.button)
                    
                    elif event.type == pygame.JOYBUTTONUP:
                        self.handle_button_release(event.button)
                    
                    elif event.type == pygame.JOYHATMOTION:
                        # D-Pad handling via HAT (hat 0 for F310)
                        if event.hat == 0:
                            x, y = event.value
                            
                            # Handle X-axis (left/right)
                            if x == 0 and self.dpad_state['x'] != 0:
                                # D-pad X released
                                self.stop_movement("X")
                            elif x != 0:
                                # D-pad X pressed
                                self.handle_axis_motion(self.AXIS_DPAD_X, float(x))
                            
                            # Handle Y-axis (up/down)
                            if y == 0 and self.dpad_state['y'] != 0:
                                # D-pad Y released
                                self.stop_movement("Y")
                            elif y != 0:
                                # D-pad Y pressed
                                self.handle_axis_motion(self.AXIS_DPAD_Y, float(y))
                            
                            # Update dpad state
                            self.dpad_state['x'] = x
                            self.dpad_state['y'] = y
                
                # Cap at 60 Hz polling rate
                clock.tick(60)
        
        except Exception as e:
            print(f"Error in joystick handler: {e}")
            self.status_changed.emit(f"Error: {e}")
        
        finally:
            self.running = False
    
    def stop(self):
        """Stop the joystick handler"""
        self.running = False
        self.wait()  # Wait for thread to finish


if __name__ == "__main__":
    # Test the joystick handler standalone
    from PyQt5.QtWidgets import QApplication
    
    def test_callback(cmd):
        print(f"Command: {cmd}")
    
    app = QApplication([])
    handler = JoystickHandler(send_command_callback=test_callback)
    handler.status_changed.connect(lambda msg: print(f"Status: {msg}"))
    handler.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
        handler.stop()
