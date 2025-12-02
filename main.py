# Ryan Seyedan - 400467887 - seyedanr - seyedanr@mcmaster.ca
#Date of file creation: 2025-04-06
#IBEHS 3H03 Project GUI for automated platform

#Updated May 2025 - Sonia Parekh

##---------------------------------------------------------------------------------

#IMPORTS
import sys #used to access system paramters like OS
from PyQt5.QtWidgets import ( 
    QApplication, QMainWindow, QPushButton, QLabel, QSlider,
    QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QGroupBox
)

from PyQt5.QtCore import Qt #for sliders
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap #for images
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit

import serial #for serial communication 
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

matplotlib.use('Agg')

class MotorControlGUI(QMainWindow): #inherits QMainWindow attributes which has all the function for creating windows
    def __init__(self): #constructor
        super().__init__() 
        self.ser = serial.Serial('COM6', 9600)
        self.ser.flush()
        self.setWindowTitle("Automated Platform Control") #window name
        #self.setStyleSheet("color: black; Background-color: light blue;")
        self.setGeometry(200, 200, 800, 650) #window dimensions
        self.initUI() #call method to setup layout and widgets 
        time.sleep(1) #delay since serial takes time to update when GUI opened
        self.update_speed()  #default speed to Arduino
        # self.teslameter = TeslameterInterface()
        self.teslameter = None



    def send_serial(self, command):
        if self.ser.is_open:
            self.ser.write((command + "\n").encode()) #arduino reads commands on new lines
            print(f"Sent: {command}")

    def closeEvent(self, event):
        if self.ser and self.ser.is_open:
            self.ser.close()
        if self.teslameter:
            self.teslameter.close()

    def update_speed(self):
        value_mm_s = float(self.speed_input.text())
        self.speed_label.setText(f"Speed: {value_mm_s:.1f} mm/s")
        
        #Conversion
        steps_per_rev = 800  #defines by TB6600
        pulley_diameter_cm = 1.3 #defines from pulley
        pulley_circumference = math.pi * pulley_diameter_cm #2*pi*r = pi*d
        steps_per_cm = steps_per_rev / pulley_circumference

        # Calculate speed and delay
        steps_per_sec = value_mm_s * (steps_per_cm/10) #multiply slider value (cm/s) by steps/cm to get steps/s
        delay_microseconds = int((1/ steps_per_sec)*1_000_000) #time it takes to step once in microseconds

        # Send delay to Arduino
        #time.sleep(1)
        self.send_serial(f"SPD:{delay_microseconds}")
        #time.sleep(1)

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
        main_layout = QVBoxLayout() # define vertical box layout mannager
                                    # this stacks widgets vertically from top to bottom
        main_layout.setSpacing(10)  # More vertical space between sections


        #crteate title bar
        self.title_label = QLabel("Automated Platform Controller")
        font = self.title_label.font()
        font.setPointSize(18)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.title_label.setContentsMargins(0, 10, 0, 10)

        #define image one
        self.image_label1 = QLabel()
        pixmap = QPixmap("HeartLabLogo.png") 
        pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation)  
        self.image_label1.setPixmap(pixmap)        

        #define image
        self.image_label2 = QLabel()
        pixmap = QPixmap("McMasterUniLogo.png")  
        pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation) 
        self.image_label2.setPixmap(pixmap)  

        #create horizontal layout and add widgets to top bar 
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.image_label1)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.image_label2)

        #Magnet Orientation Controls bar
        magnet_group = QGroupBox("Magnet Orientation") #creates container 
        magnet_layout = QHBoxLayout() #create horizontal layout 
        #label buttons
        self.roll_ccw_btn = QPushButton("↺ Roll CCW")
        self.roll_cw_btn = QPushButton("↻ Roll CW")
        self.yaw_ccw_btn = QPushButton("🔃 Yaw CCW")
        self.yaw_cw_btn = QPushButton("🔄 Yaw CW")
        #add all these buttons to the magnet layout
        for i in [self.roll_ccw_btn, self.roll_cw_btn, self.yaw_ccw_btn, self.yaw_cw_btn]:
            magnet_layout.addWidget(i) 
        magnet_group.setLayout(magnet_layout) #add layout to magnet container

        #Axis Movement Controls
        axis_group = QGroupBox("Axis Controls") #create container
        axis_layout = QGridLayout() #create grid layout

        #define buttons
        self.x_left_btn = QPushButton("⏭️ Forwards")
        self.x_right_btn = QPushButton("⏮️ Backwards")
        self.y_up_btn = QPushButton("⬆️ Right") #originally left
        self.y_down_btn = QPushButton("⬇ Left") #originally right
        self.z_up_btn = QPushButton("🔼 Up")
        self.z_down_btn = QPushButton("🔽 Down")
        self.start_btn = QPushButton("🏁 Start")
        self.stop_btn = QPushButton("⏹️ Stop")

       #define location in matrix
        axis_layout.addWidget(QLabel("X-Axis"), 0, 0)
        axis_layout.addWidget(self.x_left_btn, 1, 0)
        axis_layout.addWidget(self.x_right_btn, 2, 0)

        axis_layout.addWidget(QLabel("Y-Axis"), 0, 1)
        axis_layout.addWidget(self.y_up_btn, 1, 1)
        axis_layout.addWidget(self.y_down_btn, 2, 1)

        axis_layout.addWidget(QLabel("Z-Axis"), 0, 2)
        axis_layout.addWidget(self.z_up_btn, 1, 2)
        axis_layout.addWidget(self.z_down_btn, 2, 2)

        axis_layout.addWidget(QLabel("Measure Field"),0,3)
        axis_layout.addWidget(self.start_btn,1,3)
        axis_layout.addWidget(self.stop_btn,2,3)

        axis_group.setLayout(axis_layout) #add widgets to container layout

        #serial button bindings
        self.start_btn.clicked.connect(self.start_scan_sequence)

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

        self.start_btn.clicked.connect(lambda:self.send_serial("S+"))
        self.stop_btn.clicked.connect(lambda:self.send_serial("S-"))
        
        self.roll_ccw_btn.pressed.connect(lambda: self.send_serial("R-"))
        self.roll_ccw_btn.released.connect(lambda: self.send_serial("RS"))

        self.roll_cw_btn.pressed.connect(lambda: self.send_serial("R+"))
        self.roll_cw_btn.released.connect(lambda: self.send_serial("RS"))
        
        self.yaw_ccw_btn.pressed.connect(lambda: self.send_serial("W-"))
        self.yaw_ccw_btn.released.connect(lambda: self.send_serial("WS"))

        self.yaw_cw_btn.pressed.connect(lambda: self.send_serial("W+"))
        self.yaw_cw_btn.released.connect(lambda: self.send_serial("WS"))

    #define home box
        home_group = QGroupBox("Return Home")
        home_layout = QGridLayout()
        
        self.home_btn = QPushButton("🏠 Home")         
        self.exit_home_btn = QPushButton("🧳 Exit Homing")
        
        home_layout.addWidget(self.home_btn, 0,0)
        home_layout.addWidget(self.exit_home_btn, 0,1)

        home_group.setLayout(home_layout)

    #home serial button binding
        self.home_btn.clicked.connect(self.return_home_sequence)
        self.exit_home_btn.clicked.connect(lambda:self.send_serial("H-"))

    #define speed input box 
        speed_group = QGroupBox("Control")
        speed_layout = QHBoxLayout()

        self.speed_label = QLabel("Speed: -- mm/s")

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter speed in mm/s (e.g. 30)")
        self.speed_input.setFixedWidth(150) #input box width
        self.speed_input.setText("50")  #default box value

        # Update speed
        self.speed_input.returnPressed.connect(self.update_speed) #when enter is pressed 
        
        self.move_x = QLineEdit()
        self.move_y = QLineEdit()
        
        self.move_x.setFixedWidth(150)
        self.move_x.setPlaceholderText("Move X in mm (e.g. 20)")
        self.move_x.setText("50")
        self.move_x.returnPressed.connect(self.move_x_for) #when enter is pressed 

        self.move_y.setFixedWidth(150)
        self.move_y.setPlaceholderText("Move Y in mm (e.g. 20)")
        self.move_y.setText("50")
        self.move_y.returnPressed.connect(self.move_y_for) #when enter is pressed


        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.move_x)
        speed_layout.addWidget(self.move_y)
        speed_group.setLayout(speed_layout)


        #------------------------------------

        #Add widgets to main layout
        main_layout.addLayout(title_layout)
        main_layout.addWidget(home_group)
        main_layout.addWidget(magnet_group)
        main_layout.addWidget(axis_group)
        main_layout.addWidget(speed_group)

        #------------------------------------

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

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
        #Open the file & log
            with open(file_path, 'w') as file:
                teslameter.log_buffered_data_to_file(145, 100, file)  #duration (seconds), 10 ms timestep
                #CHANGE THE TIME ABOVE FOR DIFFERENT BOX SIZES
    
            # Wait for Arduino to complete movement
                while True:
                    if self.ser.in_waiting:
                        line = self.ser.readline().decode().strip()
                        print("Arduino:", line)
                        if line == "Completed!" or line == "Scan Stopped!":
                            break
                    time.sleep(0.1)
                    
            plot_thread = threading.Thread(target=self.plot_field, args=(file_path,), daemon = True)
            plot_thread.start()
            self.plot_field(file_path)

        except Exception as e:
            print(f"Scan/logging error: {e}")
        finally:
            self.scanning = False
        
            
    def plot_field(self, file_path):
        # Parameters
        boxsize = 50  # mm
        increment = 5  # mm
        num_points = int(boxsize / increment)  # 10
        total_points = num_points ** 3


        df = pd.read_csv(file_path, on_bad_lines='skip')
        df.columns = ["time_elapsed", "date", "time", "magnitude", "Bx", "By", "Bz", "junk1", "junk2"]

        df = df.head(total_points) # takes only the necessary points

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
        scale=1e5
        colors = cm.viridis((norm - norm.min()) / (norm.max() - norm.min()))
        ax.quiver(x, y, z, u_norm, v_norm, w_norm, normalize=False, color=colors, length=2)


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
        thread.daemon = True #daemon threads shut down when program exits
        thread.start()
    
    def move_home(self):
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


#Run the app
def window():
    app = QApplication(sys.argv) #config setup for application (for OS)
    win = MotorControlGUI()
    win.show()
    sys.exit(app.exec_()) #creates a clean exit

window()



