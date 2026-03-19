# Ryan Seyedan - 400467887 - seyedanr - seyedanr@mcmaster.ca
# Date of file creation: 2025-04-06
# IBEHS 3H03 Project GUI for automated platform

# Updated May 2025 - Sonia Parekh

# ---------------------------------------------------------------------------------

# IMPORTS
import sys  # used to access system paramters like OS
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QSlider,
    QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QGroupBox
)

from PyQt5.QtCore import Qt  # for sliders
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap  # for images
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit

import serial  # for serial communication
import serial.tools.list_ports
import threading
import time
import math

import threading
import traceback
import io
import os
import time
from lakeshore import Teslameter
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from teslameter import TeslameterInterface
from joystick_handler import JoystickHandler

matplotlib.use('Agg')


# inherits QMainWindow attributes which has all the function for creating windows
class MotorControlGUI(QMainWindow):
    def __init__(self):  # constructor
        super().__init__()
        self.ser = None  # Initialize serial as None
        self.setWindowTitle("Automated Platform Control")  # window name
        # self.setStyleSheet("color: black; Background-color: light blue;")
        self.setGeometry(200, 200, 800, 650)  # window dimensions
        
        # Initialize joystick handler
        self.joystick_handler = JoystickHandler(send_command_callback=self.send_serial)
        self.joystick_handler.status_changed.connect(self.update_joystick_status)
        self.joystick_status_label = None
        
        self.initUI()  # call method to setup layout and widgets
        # self.teslameter = TeslameterInterface()
        self.teslameter = None
        
        # Start joystick handler thread
        self.joystick_handler.start()

    def send_serial(self, command):
        if self.ser and self.ser.is_open:
            # arduino reads commands on new lines
            self.ser.write((command + "\n").encode())
            print(f"Sent: {command}")

    def closeEvent(self, event):
        if self.joystick_handler:
            self.joystick_handler.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
        if self.teslameter:
            self.teslameter.close()

    def update_joystick_status(self, status_message):
        """Update the joystick status label with the given message"""
        if self.joystick_status_label:
            self.joystick_status_label.setText(f"🎮 {status_message}")
            print(f"Joystick Status: {status_message}")

    def get_available_ports(self):
        """Get list of available COM ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def refresh_ports(self):
        """Refresh the COM port dropdown with available ports"""
        self.com_port_dropdown.clear()
        ports = self.get_available_ports()
        if ports:
            self.com_port_dropdown.addItems(ports)
            self.connection_status_label.setText("Status: Not Connected")
        else:
            self.com_port_dropdown.addItem("No ports found")
            self.connection_status_label.setText("Status: No ports available")

    def connect_serial(self):
        """Connect to the selected COM port"""
        if self.ser and self.ser.is_open:
            # Already connected, disconnect first
            self.disconnect_serial()
            return

        selected_port = self.com_port_dropdown.currentText()
        if selected_port == "No ports found" or not selected_port:
            self.connection_status_label.setText("Status: No port selected")
            return

        try:
            self.ser = serial.Serial(selected_port, 9600, timeout=1)
            self.ser.flush()
            time.sleep(1)  # delay since serial takes time to initialize
            self.update_speed()  # default speed to Arduino
            self.connection_status_label.setText(f"Status: Connected to {selected_port}")
            self.connect_btn.setText("Disconnect")
            self.com_port_dropdown.setEnabled(False)
            self.refresh_btn.setEnabled(False)
            print(f"Successfully connected to {selected_port}")
        except Exception as e:
            self.connection_status_label.setText(f"Status: Connection failed")
            print(f"Error connecting to {selected_port}: {e}")
            self.ser = None

    def disconnect_serial(self):
        """Disconnect from the current COM port"""
        if self.ser and self.ser.is_open:
            port_name = self.ser.port
            self.ser.close()
            self.ser = None
            self.connection_status_label.setText("Status: Disconnected")
            self.connect_btn.setText("Connect")
            self.com_port_dropdown.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            print(f"Disconnected from {port_name}")

    def update_speed(self):
        value_mm_s = float(self.speed_input.text())
        self.speed_label.setText(f"Speed: {value_mm_s:.1f} mm/s")

        # Conversion
        steps_per_rev = 800  # defines by TB6600
        pulley_diameter_cm = 1.3  # defines from pulley
        pulley_circumference = math.pi * pulley_diameter_cm  # 2*pi*r = pi*d
        steps_per_cm = steps_per_rev / pulley_circumference

        # Calculate speed and delay
        # multiply slider value (cm/s) by steps/cm to get steps/s
        steps_per_sec = value_mm_s * (steps_per_cm/10)
        # time it takes to step once in microseconds
        delay_microseconds = int((1 / steps_per_sec)*1_000_000)

        # Send delay to Arduino
        # time.sleep(1)
        # print(delay_microseconds)
        self.send_serial(f"SPD:{delay_microseconds}")
        # time.sleep(1)

    def move_x_for(self):
        steps = int(self.move_x.text())
        if steps < 0:
            for i in range(-steps):
                self.send_serial("X+")
                self.send_serial("XS")
        else:
            for i in range(steps):
                self.send_serial("X-")
                self.send_serial("XS")

    def move_y_for(self):
        moves = 24
        step_each_move = 50
        steps = int(self.move_y.text())
        for i in range(moves):
            for j in range(28):
                if i % 2 == 0:
                    for s in range(step_each_move):
                        self.send_serial("Y-")
                        self.send_serial("YS")
                else:
                    for s in range(step_each_move):
                        self.send_serial("Y+")
                        self.send_serial("YS")
                time.sleep(0.1)
                self.teslameter.scan_to_file(i, j)
                time.sleep(0.1)
            for s in range(60):
                self.send_serial("X+")
                self.send_serial("XS")
        # if steps < 0:
        #     for i in range(-steps):
        #         self.send_serial("Y+")
        #         self.send_serial("YS")
        #         time.sleep(0.1)
        #         self.teslameter.scan_to_file(steps, 0)
        #         time.sleep(0.1)
        # else:
        #     for i in range(step_each_move):
        #         self.send_serial("Y-")
        #         self.send_serial("YS")

    def initUI(self):
        main_layout = QVBoxLayout()  # define vertical box layout mannager
        # this stacks widgets vertically from top to bottom
        main_layout.setSpacing(10)  # More vertical space between sections

        # crteate title bar
        self.title_label = QLabel("Automated Platform Controller")
        font = self.title_label.font()
        font.setPointSize(18)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.title_label.setContentsMargins(0, 10, 0, 10)

        # define image one
        self.image_label1 = QLabel()
        pixmap = QPixmap("assets/HeartLabLogo.png")
        pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation)
        self.image_label1.setPixmap(pixmap)

        # define image
        self.image_label2 = QLabel()
        pixmap = QPixmap("assets/McMasterUniLogo.png")
        pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation)
        self.image_label2.setPixmap(pixmap)

        # create horizontal layout and add widgets to top bar
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.image_label1)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.image_label2)

        # Magnet Orientation Controls bar
        magnet_group = QGroupBox("Magnet Orientation")  # creates container
        magnet_layout = QHBoxLayout()  # create horizontal layout
        # label buttons
        self.roll_ccw_btn = QPushButton("↺ Roll CCW")
        self.roll_cw_btn = QPushButton("↻ Roll CW")
        self.yaw_ccw_btn = QPushButton("🔃 Yaw CCW")
        self.yaw_cw_btn = QPushButton("🔄 Yaw CW")
        # add all these buttons to the magnet layout
        for i in [self.roll_ccw_btn, self.roll_cw_btn, self.yaw_ccw_btn, self.yaw_cw_btn]:
            magnet_layout.addWidget(i)
        magnet_group.setLayout(magnet_layout)  # add layout to magnet container

        # Axis Movement Controls
        axis_group = QGroupBox("Axis Controls")  # create container
        axis_layout = QGridLayout()  # create grid layout

        # define buttons
        self.x_left_btn = QPushButton("⏭️ Forwards")
        self.x_right_btn = QPushButton("⏮️ Backwards")
        self.y_up_btn = QPushButton("⬆️ Right")  # originally left
        self.y_down_btn = QPushButton("⬇ Left")  # originally right
        self.z_up_btn = QPushButton("🔼 Up")
        self.z_down_btn = QPushButton("🔽 Down")
        self.start_btn = QPushButton("🏁 Start")
        self.stop_btn = QPushButton("⏹️ Stop")
        self.plot_infinity_btn = QPushButton("Plot Infinity")

       # define location in matrix
        axis_layout.addWidget(QLabel("X-Axis"), 0, 0)
        axis_layout.addWidget(self.x_left_btn, 1, 0)
        axis_layout.addWidget(self.x_right_btn, 2, 0)

        axis_layout.addWidget(QLabel("Y-Axis"), 0, 1)
        axis_layout.addWidget(self.y_up_btn, 1, 1)
        axis_layout.addWidget(self.y_down_btn, 2, 1)

        axis_layout.addWidget(QLabel("Z-Axis"), 0, 2)
        axis_layout.addWidget(self.z_up_btn, 1, 2)
        axis_layout.addWidget(self.z_down_btn, 2, 2)

        axis_layout.addWidget(QLabel("Measure Field"), 0, 3)
        axis_layout.addWidget(self.start_btn, 1, 3)
        axis_layout.addWidget(self.stop_btn, 2, 3)
        axis_layout.addWidget(self.plot_infinity_btn, 3, 3)

        axis_group.setLayout(axis_layout)  # add widgets to container layout

        # serial button bindings
        self.start_btn.clicked.connect(self.follow_path_sequence)
        self.stop_btn.clicked.connect(self.follow_path_sequence2)

        self.x_left_btn.pressed.connect(lambda: self.send_serial("X-"))
        self.x_left_btn.released.connect(lambda: self.send_serial("XS"))

        self.x_right_btn.pressed.connect(lambda: self.send_serial("X+"))
        self.x_right_btn.released.connect(lambda: self.send_serial("XS"))

        self.y_up_btn.pressed.connect(lambda: self.send_serial("Y+"))
        self.y_up_btn.released.connect(lambda: self.send_serial("YS"))

        self.y_down_btn.pressed.connect(lambda: self.send_serial("Y-"))
        self.y_down_btn.released.connect(lambda: self.send_serial("YS"))

        self.z_up_btn.pressed.connect(lambda: self.send_serial("Z+"))
        self.z_up_btn.released.connect(lambda: self.send_serial("ZS"))

        self.z_down_btn.pressed.connect(lambda: self.send_serial("Z-"))
        self.z_down_btn.released.connect(lambda: self.send_serial("ZS"))

        # self.start_btn.clicked.connect(lambda: self.send_serial("S+"))
        # self.stop_btn.clicked.connect(lambda: self.send_serial("S-"))

        self.roll_ccw_btn.pressed.connect(lambda: self.send_serial("R-"))
        self.roll_ccw_btn.released.connect(lambda: self.send_serial("RS"))

        self.roll_cw_btn.pressed.connect(lambda: self.send_serial("R+"))
        self.roll_cw_btn.released.connect(lambda: self.send_serial("RS"))

        self.yaw_ccw_btn.pressed.connect(lambda: self.send_serial("W-"))
        self.yaw_ccw_btn.released.connect(lambda: self.send_serial("WS"))

        self.yaw_cw_btn.pressed.connect(lambda: self.send_serial("W+"))
        self.yaw_cw_btn.released.connect(lambda: self.send_serial("WS"))

        # plotting button binding
        # self.plot_infinity_btn.clicked.connect(self.handle_plot_infinity)

    # define home box
        home_group = QGroupBox("Return Home")
        home_layout = QGridLayout()

        self.home_btn = QPushButton("🏠 Home")
        self.exit_home_btn = QPushButton("🧳 Exit Homing")

        home_layout.addWidget(self.home_btn, 0, 0)
        home_layout.addWidget(self.exit_home_btn, 0, 1)

        home_group.setLayout(home_layout)

    # home serial button binding
        self.home_btn.clicked.connect(lambda: self.start_follow_path_thread(self.draw_infinity))
        self.exit_home_btn.clicked.connect(lambda: self.send_serial("H-"))

    # define speed input box
        speed_group = QGroupBox("Control")
        speed_layout = QHBoxLayout()

        self.speed_label = QLabel("Speed: -- mm/s")

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter speed in mm/s (e.g. 30)")
        self.speed_input.setFixedWidth(150)  # input box width
        self.speed_input.setText("100")  # default box value

        # Update speed
        self.speed_input.returnPressed.connect(
            self.update_speed)  # when enter is pressed

        self.move_x = QLineEdit()
        self.move_y = QLineEdit()

        self.move_x.setFixedWidth(150)
        self.move_x.setPlaceholderText("Move X in mm (e.g. 20)")
        self.move_x.setText("50")
        self.move_x.returnPressed.connect(
            self.move_x_for)  # when enter is pressed

        self.move_y.setFixedWidth(150)
        self.move_y.setPlaceholderText("Move Y in mm (e.g. 20)")
        self.move_y.setText("50")
        self.move_y.returnPressed.connect(
            self.move_y_for)  # when enter is pressed

        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.move_x)
        speed_layout.addWidget(self.move_y)
        speed_group.setLayout(speed_layout)

        # COM Port Connection Group
        connection_group = QGroupBox("Serial Connection")
        connection_layout = QHBoxLayout()
        
        connection_layout.addWidget(QLabel("COM Port:"))
        self.com_port_dropdown = QComboBox()
        self.com_port_dropdown.setMinimumWidth(120)
        connection_layout.addWidget(self.com_port_dropdown)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        connection_layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_serial)
        connection_layout.addWidget(self.connect_btn)
        
        self.connection_status_label = QLabel("Status: Not Connected")
        connection_layout.addWidget(self.connection_status_label)
        connection_layout.addStretch()
        
        connection_group.setLayout(connection_layout)
        
        # Populate COM ports on startup
        self.refresh_ports()

        # Joystick Status Group
        joystick_group = QGroupBox("Joystick Status")
        joystick_layout = QHBoxLayout()
        self.joystick_status_label = QLabel("🎮 Initializing joystick...")
        joystick_layout.addWidget(self.joystick_status_label)
        joystick_group.setLayout(joystick_layout)

        # ------------------------------------

        # Add widgets to main layout
        main_layout.addLayout(title_layout)
        main_layout.addWidget(connection_group)
        main_layout.addWidget(joystick_group)
        main_layout.addWidget(home_group)
        main_layout.addWidget(magnet_group)
        main_layout.addWidget(axis_group)
        main_layout.addWidget(speed_group)

        # Tracking controls
        track_group = QGroupBox("Tracking Shapes")
        track_layout = QGridLayout()
        
        track_triangle_label_layout = QHBoxLayout()
        track_triangle_label_layout.addWidget(QLabel("Sidelength (mm):"))
        track_triangle_label_layout.addWidget(QLineEdit())
        track_layout.addLayout(track_triangle_label_layout, 0, 0)
        
        self.track_triangle_btn = QPushButton("Track Triangle")
        track_layout.addWidget(self.track_triangle_btn, 1, 0)
        
        track_square_label_layout = QHBoxLayout()
        track_square_label_layout.addWidget(QLabel("Sidelength (mm):"))
        track_square_label_layout.addWidget(QLineEdit())
        track_layout.addLayout(track_square_label_layout, 0, 1)
        
        self.track_square_btn = QPushButton("Track Square")
        track_layout.addWidget(self.track_square_btn, 1, 1)
        
        track_circle_label_layout = QHBoxLayout()
        track_circle_label_layout.addWidget(QLabel("Radius (mm):"))
        track_circle_label_layout.addWidget(QLineEdit())
        track_layout.addLayout(track_circle_label_layout, 0, 2)
        self.track_circle_btn = QPushButton("Track Circle")
        track_layout.addWidget(self.track_circle_btn, 1, 2)
        
        track_infinity_label_layout = QHBoxLayout()
        track_infinity_label_layout.addWidget(QLabel("Scale (mm):"))
        track_infinity_label_layout.addWidget(QLineEdit())
        track_layout.addLayout(track_infinity_label_layout, 0, 3)
        self.track_infinity_btn = QPushButton("Track Infinity")
        track_layout.addWidget(self.track_infinity_btn, 1, 3)
        
        track_group.setLayout(track_layout)
        main_layout.addWidget(track_group)
        
        # axis_layout.addWidget(QLabel("Z-Axis"), 0, 2)
        # axis_layout.addWidget(self.z_up_btn, 1, 2)
        # axis_layout.addWidget(self.z_down_btn, 2, 2)

        # ------------------------------------

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # add keyboard controls

    def keyPressEvent(self, event):
        key = event.key()
        # print(f"Key pressed: {key}")
        if key == Qt.Key_A:
            self.send_serial("Y+")
        elif key == Qt.Key_D:
            self.send_serial("Y-")
        elif key == Qt.Key_W:
            self.send_serial("X-")
        elif key == Qt.Key_S:
            self.send_serial("X+")
        elif key == Qt.Key_Q:
            self.send_serial("Z+")
        elif key == Qt.Key_E:
            self.send_serial("Z-")
        elif key == Qt.Key_Z:
            self.send_serial("R-")
        elif key == Qt.Key_C:
            self.send_serial("R+")
        elif key == Qt.Key_N:
            self.send_serial("W+")
        elif key == Qt.Key_M:
            self.send_serial("W-")
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        key = event.key()
        # print(f"Key released: {key}")
        if key == Qt.Key_A or key == Qt.Key_D:
            self.send_serial("YS")
        elif key == Qt.Key_W or key == Qt.Key_S:
            self.send_serial("XS")
        elif key == Qt.Key_Q or key == Qt.Key_E:
            self.send_serial("ZS")
        elif key == Qt.Key_Z or key == Qt.Key_C:
            self.send_serial("RS")
        elif key == Qt.Key_N or key == Qt.Key_M:
            self.send_serial("WS")
        super().keyReleaseEvent(event)

    def move_forward_for(self, time):
        self.send_serial("X-")
        time.sleep(time)
        self.send_serial("XS")
    def move_backward_for(self, time):
        self.send_serial("X+")
        time.sleep(time)
        self.send_serial("XS")
    def move_left_for(self, time):
        self.send_serial("Y+")
        time.sleep(time)
        self.send_serial("YS")
    def move_right_for(self, time):
        self.send_serial("Y-")
        time.sleep(time)
        self.send_serial("YS")
        
    
    def follow_path_sequence2(self):
        self.send_serial("X+")
        time.sleep(0.05)
        self.send_serial("XS")

    def follow_path_sequence(self):
        radius = 200  # mm
        center_x = 150  # mm
        center_y = 150  # mm
        num_points = 30  # one point per degree for smooth circular motion
        
        current_x = 150+radius  # mm (starting at center)
        current_y = 150  # mm (starting at center)
        
        for i in range(num_points + 1):
            angle = 2 * math.pi * i / num_points
            target_x = center_x + radius * math.cos(angle)
            target_y = center_y + radius * math.sin(angle)

            dx = target_x - current_x
            dy = target_y - current_y
            # print(dx, dy)
            # continue

            # Move in 1mm steps to reach target
            while abs(dx) > 0.5 or abs(dy) > 0.5:  # threshold for rounding errors
                # Determine which axis to move (prioritize the one with larger distance)
                # if abs(dx) > abs(dy):
                if dx > 0:
                    self.send_serial("X-")  # move forward (positive X)
                    current_x += 1
                else:
                    self.send_serial("X+")  # move backward (negative X)
                    current_x -= 1
            # else:
                if dy > 0:
                    self.send_serial("Y+")  # move right (positive Y)
                    current_y += 1
                else:
                    self.send_serial("Y-")  # move left (negative Y)
                    current_y -= 1
            
                
                # Recalculate remaining distance
                dx = target_x - current_x
                dy = target_y - current_y
            
    def handle_plot_infinity(self):
        try:
            saved = self.plot_infinity(center_x=0, center_y=0, scale=800, segments=360)
            print(f"Infinity plot saved: {saved}")
        except Exception as e:
            print(f"Failed to plot infinity: {e}")

    def start_follow_path_thread(self, function):
        thread = threading.Thread(target=function)
        thread.daemon = True  # daemon threads shut down when program exits
        thread.start()  
        
    def draw_circle(self) -> None:

        radius = 800  # mm
        center_x = 0  # mm
        center_y = 0  # mm
        num_points = 100  # one point per degree for smooth circular motion
        current_x = center_x + radius
        current_y = center_y

        for i in range(num_points + 1):
            angle = 2 * math.pi * i / num_points
            target_x = center_x + radius * math.cos(angle)
            target_y = center_y + radius * math.sin(angle)

            dx = target_x - current_x
            dy = target_y - current_y

            # Step until close enough to target (0.5 mm tolerance)
            while abs(dx) > 0.5 or abs(dy) > 0.5:
                # Step X axis by 1 mm toward target
                if abs(dx) > 0.5:
                    if dx > 0:
                        self.send_serial("X-")
                        current_x += 1
                    else:
                        self.send_serial("X+")
                        current_x -= 1
                    # self.send_serial("XS")
                    # if step_delay_s > 0:
                        # time.sleep(step_delay_s)

                # Step Y axis by 1 mm toward target
                if abs(dy) > 0.5:
                    if dy > 0:
                        self.send_serial("Y+")
                        current_y += 1
                    else:
                        self.send_serial("Y-")
                        current_y -= 1
                    # self.send_serial("YS")
                    # if step_delay_s > 0:
                        # time.sleep(step_delay_s)

                # Recompute remaining delta
                dx = target_x - current_x
                dy = target_y - current_y

    def draw_infinity(self):
        """
        Draw an infinity symbol (lemniscate) using 1mm axis steps.

        Uses the parametric equation of a lemniscate:
        - x = a * cos(t) / (1 + sin²(t))
        - y = a * sin(t) * cos(t) / (1 + sin²(t))

        Parameters:
        - center_x, center_y: Offset/center point in mm (software reference).
        - scale: Scale factor (a) in mm; controls the overall size.
        - segments: Number of points around the curve to sample.
        """
        center_x = 0
        center_y = 0
        scale = 1000
        segments = 200

        current_x = scale
        current_y = 0

        for i in range(segments + 1):
            t = 2 * math.pi * i / segments
            
            # Lemniscate parametric equations
            denominator = 1 + math.sin(t) ** 2
            target_x = center_x + scale * math.cos(t) / denominator
            target_y = center_y + scale * math.sin(t) * math.cos(t) / denominator

            dx = target_x - current_x
            dy = target_y - current_y

            # Step until close enough to target (0.5 mm tolerance)
            while abs(dx) > 0.5 or abs(dy) > 0.5:
                # Step X axis by 1 mm toward target
                if abs(dx) > 0.5:
                    if dx > 0:
                        self.send_serial("X-")
                        current_x += 1
                    else:
                        self.send_serial("X+")
                        current_x -= 1

                # Step Y axis by 1 mm toward target
                if abs(dy) > 0.5:
                    if dy > 0:
                        self.send_serial("Y+")
                        current_y += 1
                    else:
                        self.send_serial("Y-")
                        current_y -= 1

                # Recompute remaining delta
                dx = target_x - current_x
                dy = target_y - current_y

    def plot_infinity(self, center_x: float = 0, center_y: float = 0,
                      scale: float = 100, segments: int = 360,
                      save_path: str = None) -> str:
        """
        Plot an infinity symbol (lemniscate) and save the figure.

        Uses the parametric equations:
        - x = a * cos(t) / (1 + sin^2(t))
        - y = a * sin(t) * cos(t) / (1 + sin^2(t))

        Parameters:
        - center_x, center_y: Offset center in mm for plotting.
        - scale: Scale factor (a) in mm controlling size.
        - segments: Number of sampled points along the curve.
        - save_path: Optional path to save the PNG; defaults to results/infinity.png.

        Returns:
        - The path where the image was saved.
        """

        xs = []
        ys = []
        for i in range(segments + 1):
            t = 2 * math.pi * i / segments
            denom = 1 + math.sin(t) ** 2
            x = center_x + scale * math.cos(t) / denom
            y = center_y + scale * math.sin(t) * math.cos(t) / denom
            xs.append(x)
            ys.append(y)
        
        print(xs[:10], ys[:10])  # Debug: print first 10 points

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.plot(xs, ys, '-', linewidth=2)
        ax.set_aspect('equal', 'box')
        ax.set_xlabel('X [mm]')
        ax.set_ylabel('Y [mm]')
        ax.set_title('Infinity (Lemniscate)')
        ax.grid(True, alpha=0.3)

        if save_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            save_path = os.path.join(script_dir, 'results', 'infinity.png')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        plt.tight_layout()
        fig.savefig(save_path)
        plt.close(fig)
        print(f"Saved infinity plot to: {save_path}")
        return save_path

    def follow_triangle_path(self):
        side_length = 100  # mm
        points_per_side = 10  # number of points to move per side for smoothness
        
        # Define triangle vertices
        p1 = (0, 0)
        p2 = (math.sqrt(3) / 2 * side_length, side_length/2)
        p3 = (0, side_length)
        
        sleep_time = 4  # time to move between points

        self.send_serial("X-")
        self.send_serial("Y-")
        time.sleep(sleep_time)
        self.send_serial("XS")
        self.send_serial("YS")
        
        self.send_serial("X+")
        self.send_serial("Y-")
        time.sleep(sleep_time)
        self.send_serial("XS")
        self.send_serial("YS")
        
        self.send_serial("Y+")
        time.sleep(sleep_time)
        self.send_serial("YS")
                
    def follow_square_path(self):

        sleep_time = 3.5  # time to move between points

        self.send_serial("X-")
        time.sleep(sleep_time)
        self.send_serial("XS")
        
        self.send_serial("Y-")
        time.sleep(sleep_time)
        self.send_serial("YS")
        
        self.send_serial("X+")
        time.sleep(sleep_time)
        self.send_serial("XS")
        
        self.send_serial("Y+")
        time.sleep(sleep_time)
        self.send_serial("YS")

    def start_scan_sequence(self):
        self.send_serial("S+")
        thread = threading.Thread(target=self._scan_and_log)
        thread.daemon = True
        thread.start()

    def _scan_and_log(self):
        self.scanning = True
        try:
            # Connect to the Teslameter
            teslameter = Teslameter()
            teslameter.command('SENSE:MODE DC')
            serial_no = teslameter.query('PROBE:SNUMBER?')
            print(f"Connected to probe: {serial_no}")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "field_map_data.csv")
        # Open the file & log
            with open(file_path, 'w') as file:
                # duration (seconds), 10 ms timestep
                teslameter.log_buffered_data_to_file(145, 100, file)
                # CHANGE THE TIME ABOVE FOR DIFFERENT BOX SIZES

            # Wait for Arduino to complete movement
                while True:
                    if self.ser.in_waiting:
                        line = self.ser.readline().decode().strip()
                        print("Arduino:", line)
                        if line == "Completed!" or line == "Scan Stopped!":
                            break
                    time.sleep(0.1)

            plot_thread = threading.Thread(
                target=self.plot_field, args=(file_path,), daemon=True)
            plot_thread.start()
            self.plot_field(file_path)

        except Exception as e:
            print(f"Scan/logging error: {e}")
        finally:
            self.scanning = False

    # def plot_field(self, file_path):
        # Parameters
        boxsize = 50  # mm
        increment = 5  # mm
        num_points = int(boxsize / increment)  # 10
        total_points = num_points ** 3

        df = pd.read_csv(file_path, on_bad_lines='skip')
        df.columns = ["time_elapsed", "date", "time",
                      "magnitude", "Bx", "By", "Bz", "junk1", "junk2"]

        df = df.head(total_points)  # takes only the necessary points

        # Position grid (same order as Arduino movement)
        x_vals = np.arange(0, boxsize, increment)
        y_vals = np.arange(0, boxsize, increment)
        z_vals = np.arange(0, boxsize, increment)
        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')

        # Flatten a nested list into a single list
        df["x"] = X.flatten()
        df["y"] = Y.flatten()
        df["z"] = Z.flatten()

        # creating vectors (magnitude)
        u = df["Bx"].astype(float).values
        v = df["By"].astype(float).values
        w = df["Bz"].astype(float).values

        # getting vector positions (direction)
        x = df["x"].values
        y = df["y"].values
        z = df["z"].values

        mag = df['magnitude'].to_numpy()

        # Normalize vectors for display
        norm = np.sqrt(u**2 + v**2 + w**2)
        u_norm = u / norm
        v_norm = v / norm
        w_norm = w / norm

        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        scale = 1e5
        colors = cm.viridis((norm - norm.min()) / (norm.max() - norm.min()))
        ax.quiver(x, y, z, u_norm, v_norm, w_norm,
                  normalize=False, color=colors, length=2)

        mappable = plt.cm.ScalarMappable(cmap=cm.viridis)
        mappable.set_array(norm)  # Use actual magnitude norm for colorbar
        cbar = plt.colorbar(mappable, ax=ax, pad=0.1)
        cbar.set_label('Field Magnitude [mT]')

        ax.set_xlabel('X [mm]')
        ax.set_ylabel('Y [mm]')
        ax.set_zlabel('Z [mm]')
        ax.set_title('3D Magnetic Field Quiver Plot')
        plt.tight_layout()
        plt.savefig("mygraph.png")

    def return_home_sequence(self):
        self.send_serial("H+")
        thread = threading.Thread(target=self.move_home)
        thread.daemon = True  # daemon threads shut down when program exits
        thread.start()

    # def move_home(self):
        self.move = True
        try:
            while True:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode().strip()
                    print("Arduino:", line)
                    if line == "Home!" or "Going Home Ended Early":
                        break
                time.sleep(0.1)
        except Exception as e:
            print("error moving home", e)
            traceback.print_exc()
        finally:
            self.move = False


# Run the app
def window():
    app = QApplication(sys.argv)  # config setup for application (for OS)
    win = MotorControlGUI()
    win.show()
    sys.exit(app.exec_())  # creates a clean exit


window()
