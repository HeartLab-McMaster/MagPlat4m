//make sure your Arduino serial monitor is closed while running the GUI — only one program can use the COM port at a time.

// Pin definitions
#define xStepRight 5
#define xDirRight 4
#define xStepLeft 7
#define xDirLeft 6
#define yStep 3
#define yDir 2                               
#define zStep 9
#define zDir 8

// State
bool moveX = false; //flags for axis movement -> false = dont move -> true = move
bool moveY = false;
bool moveZ = false;
int dirX = HIGH; //HIGH = CW -> LOW = CCW
int dirY = HIGH;
int dirZ = HIGH;

//global variables
int stepDelay; 
int halfDelay;

void setup() {
  Serial.begin(9600);
  pinMode(xStepRight, OUTPUT); //set all stepper motors direction & step pulse to outputs
  pinMode(xDirRight, OUTPUT);
  pinMode(xStepLeft, OUTPUT);
  pinMode(xDirLeft, OUTPUT);
  pinMode(yStep, OUTPUT);
  pinMode(yDir, OUTPUT);
  pinMode(yStep, OUTPUT);
  pinMode(zDir, OUTPUT);
  pinMode(zStep, OUTPUT);

}

void loop() {
  if (Serial.available()) {
    
    String cmd = Serial.readStringUntil('\n'); //checks for data on serial port

    if (cmd.startsWith("SPD:")) {
      int newDelay = cmd.substring(4).toInt();  // extract number after SPD:
      if (newDelay > 0) stepDelay = newDelay;
    }

    if (cmd == "X+") {
      dirX = HIGH;
      digitalWrite(xDirRight, dirX);
      digitalWrite(xDirLeft, dirX);
      moveX = true;
    } else if (cmd == "X-") {
      dirX = LOW;
      digitalWrite(xDirRight, dirX);
      digitalWrite(xDirLeft, dirX);
      moveX = true;
    } else if (cmd == "XS") {
      moveX = false;
    }

    else if (cmd == "Y+") {
      dirY = HIGH;
      digitalWrite(yDir, dirY);
      moveY = true;
    } else if (cmd == "Y-") {
      dirY = LOW;
      digitalWrite(yDir, dirY);
      moveY = true;
    } else if (cmd == "YS") {
      moveY = false;
    }
    else if (cmd == "Z+"){
    dirZ = HIGH;
    digitalWrite(zDir, dirZ);
    moveZ = true;
    }
    else if (cmd == "Z-"){
    dirZ = LOW;
    digitalWrite(zDir, dirZ);
    moveZ = true;
    }
    else if (cmd == "ZS"){
      moveZ = false;

    }
  }
//create a duty cycle for stepping in the X direction 
//CW or CCW is determined above based on cmd read at port
//only on the rising edge triggers a step 

  halfDelay = stepDelay / 2;

  if (moveX) { 
    digitalWrite(xStepRight, HIGH);
    digitalWrite(xStepLeft, HIGH);
    delayMicroseconds(halfDelay);
    digitalWrite(xStepRight, LOW);
    digitalWrite(xStepLeft, LOW);
    delayMicroseconds(halfDelay);
  }

  if (moveY) {
    digitalWrite(yStep, HIGH);
    delayMicroseconds(halfDelay);
    digitalWrite(yStep, LOW);
    delayMicroseconds(halfDelay);
  }

  if (moveZ)
  {
    digitalWrite(zStep, HIGH);
    delayMicroseconds(halfDelay);
    digitalWrite(zStep, LOW);
    delayMicroseconds(halfDelay);
  }
}
