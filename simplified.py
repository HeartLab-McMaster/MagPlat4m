# Ryan Seyedan - 400467887 - seyedanr - seyedanr@mcmaster.ca
#Date of file creation: 2025-04-06
#IBEHS 3H03 Project GUI for automated platform

##---------------------------------------------------------------------------------

#IMPORTS
import sys #used to access system paramters like OS
from PyQt5.QtWidgets import ( 
    QApplication, QMainWindow, QPushButton, QLabel, QSlider,
    QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QGroupBox
)
from PyQt5.QtCore import Qt #for sliders
from PyQt5.QtGui import QPixmap #for images
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit

import serial #for serial communication 
import serial.tools.list_ports
import threading
import time
import math


class MotorControlGUI(QMainWindow): #inherits QMainWindow attributes which has all the function for creating windows
    def __init__(self): #constructor
        super().__init__() 
        self.ser = None
        # self.ser.flush()
        self.setWindowTitle("Automated Platform Control") #window name
        self.setGeometry(200, 200, 800, 650) #window dimensions
        self.initUI() #call method to setup layout and widgets 
        time.sleep(1) #delay since serial takes time to update when GUI opened
        self.update_speed()  #default speed to Arduino


    def send_serial(self, command):
        return
        if self.ser.is_open:
            self.ser.write((command + "\n").encode()) #arduino reads commands on new lines
            print(f"Sent: {command}")

    def closeEvent(self, event):
        if self.ser and self.ser.is_open:
            self.ser.close()

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
        pixmap = QPixmap("assets/HeartLabLogo.png") 
        pixmap = pixmap.scaledToHeight(80, Qt.SmoothTransformation)  
        self.image_label1.setPixmap(pixmap)        

        #define image
        self.image_label2 = QLabel()
        pixmap = QPixmap("assets/McMasterUniLogo.png")  
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
        self.x_left_btn = QPushButton("⬅️ Forwards")
        self.x_right_btn = QPushButton("➡️ Backwards")
        self.y_up_btn = QPushButton("⬆️ Left")
        self.y_down_btn = QPushButton("⬇️ Right")
        self.z_up_btn = QPushButton("🔼")
        self.z_down_btn = QPushButton("🔽")

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

        axis_group.setLayout(axis_layout) #add widgets to container layout


        #serial button bindings
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

        #define speed input box 
        speed_group = QGroupBox("Speed Control")
        speed_layout = QHBoxLayout()

        self.speed_label = QLabel("Speed: -- mm/s")

        self.speed_input = QLineEdit()
        self.speed_input.setPlaceholderText("Enter speed in mm/s (e.g. 30)")
        self.speed_input.setFixedWidth(150) #input box width
        self.speed_input.setText("50")  #default box value

        # Update speed
        self.speed_input.returnPressed.connect(self.update_speed) #when enter is pressed 

        speed_layout.addWidget(self.speed_input)
        speed_layout.addWidget(self.speed_label)
        speed_group.setLayout(speed_layout)


        #------------------------------------

        #Add widgets to main layout
        main_layout.addLayout(title_layout)
        main_layout.addWidget(magnet_group)
        main_layout.addWidget(axis_group)
        main_layout.addWidget(speed_group)
        #main_layout.addWidget(self.status_label)

        #------------------------------------

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

#Run the app
def window():
    app = QApplication(sys.argv) #config setup for application (for OS)
    win = MotorControlGUI()
    win.show()
    sys.exit(app.exec_()) #creates a clean exit

window()


