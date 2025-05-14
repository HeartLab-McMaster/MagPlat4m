#imports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MyWindow(QMainWindow): #inherit from QMainWindow
    def __init__(self): #runs every time an instance of the class gets called
        super(MyWindow,self).__init__() #constructor
        self.setGeometry(200,200,300,300) #dimensions of window -> xpos,ypos,width,height
        self.setWindowTitle("Automated Platform GUI") #name of window
        self.initUI()
    
    def initUI(self):
        #create label
        self.label = QtWidgets.QLabel(self) #add it to its own object -> why self
        self.label.setText("my first label")
        self.label.move(50,50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Click ME") #text within the button
        self.b1.clicked.connect(self.clicked) #map the event ot the button press
   
    def clicked(self):
        self.label.setText("you pressed the button")
        self.update()
    
    def update(self):
        self.label.adjustSize()


#define application
def window():
    app = QApplication(sys.argv) #config setup for QS application (for OS)
    win = MyWindow() #create GUi window
    win.show()
    sys.exit(app.exec_()) #creates a clean exit

window()

