// Pin definitions
#define xStepRight 5
#define xDirRight 4
#define xStepLeft 7
#define xDirLeft 6
#define yStep 3
#define yDir 2                               
#define zStep 9
#define zDir 8

const int limitSwitchY1 = 50; // limit switch pin locations; moveYL
const int limitSwitchX1 = 51; 
const int limitSwitchY2 = 48; 
const int limitSwitchX2 = 49; 

// flags for axis movement -> false = dont move -> true = move
bool moveZ = false;
bool moveX = false;
bool moveY = false;
bool yScanDirFlag = true;

// states
bool stopMove = false;
bool scanning = false;
bool isStopped = false;

// home flags
bool goHome = false;
bool xHome = false;
bool yHome = false;

// global variables
int dirX = HIGH; //HIGH = CW -> LOW = CCW
int dirY = HIGH;
int dirZ = HIGH;

unsigned long lastCommand = 0;

int stepDelay; 
int halfDelay;

// Box Movement Variables
const int boxsize = 50; // mm
const int increment = 5; //mm
const int NumXPoints = (boxsize / increment) + 1; //steps per axis
const int stepsPerIncrement = 125; //98; //based on pitch diameter and steps/rev
const int NumYPoints = NumXPoints;
const int NumZPoints = NumXPoints;


void setup() {
  // setup code here, runs once:
  pinMode(limitSwitchY1, INPUT_PULLUP); // PULLUP based on wiring 
  pinMode(limitSwitchX1, INPUT_PULLUP);
  pinMode(limitSwitchY2, INPUT_PULLUP);
  pinMode(limitSwitchX2, INPUT_PULLUP);

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

  lastCommand = millis();
}

void loop() {

  if (Serial.available()){
    
      if (isStopped == false){
      String cmd = Serial.readStringUntil('\n'); //checks for data on serial port
      lastCommand = millis();

        if (cmd.startsWith("SPD:")){
          int newDelay = cmd.substring(4).toInt();  // extract number after SPD:
          if (newDelay > 0){
            stepDelay = newDelay;
            halfDelay = stepDelay / 2;
          } 
        }

        if (cmd == "X+"){
          dirX = HIGH;
          digitalWrite(xDirRight, dirX);
          digitalWrite(xDirLeft, dirX);
          moveX = true;}
        else if (cmd == "X-"){
          dirX = LOW;
          digitalWrite(xDirRight, dirX);
          digitalWrite(xDirLeft, dirX);
          moveX = true;} 
        else if (cmd == "XS"){
          moveX = false;}

        else if (cmd == "Y+"){
          dirY = HIGH;
          digitalWrite(yDir, dirY);
          moveY = true;}

        else if (cmd == "Y-"){
          dirY = LOW;
          digitalWrite(yDir, dirY);
          moveY = true;}
        else if (cmd == "YS"){
          moveY = false;}
        
        else if (cmd == "Z+"){
          dirZ = HIGH;
          digitalWrite(zDir, dirZ);
          moveZ = true;}
        else if (cmd == "Z-"){
          dirZ = LOW;
          digitalWrite(zDir, dirZ);
          moveZ = true;}
        else if (cmd == "ZS"){
          moveZ = false;}

        else if (cmd == "S+"){ 
          scanning = true;
          stopMove = false;}
        else if(cmd == "S-"){
          scanning = false;
          stopMove = true;}

        else if (cmd == "H+"){
          stopMove = false;
          goHome = true;
          xHome = false;
          yHome = false;
        }
      }
  
    if (goHome){ // homing commands

      while(!xHome){
        checkStopCommand();
        checkSwitchStatus();
        if (stopMove) {
          Serial.println("XHome Ended Early");
          break;
        }
        dirX = HIGH;
        digitalWrite(xDirRight, dirX);
        digitalWrite(xDirLeft, dirX);

        digitalWrite(xStepRight, HIGH);
        digitalWrite(xStepLeft, HIGH);
        delayMicroseconds(halfDelay);
        digitalWrite(xStepRight, LOW);
        digitalWrite(xStepLeft, LOW);
        delayMicroseconds(halfDelay);
      }

      while(!yHome){
        checkStopCommand();
        checkSwitchStatus();
        if (stopMove) {
          Serial.println("YHome Ended Early");
          break;
        }
        dirY = LOW;
        digitalWrite(yDir, dirY);

        digitalWrite(yStep, HIGH);
        delayMicroseconds(halfDelay);
        digitalWrite(yStep, LOW);
        delayMicroseconds(halfDelay);
      }

      if (!stopMove){
        Serial.println("Home!");
      }
      goHome = false;
      stopMove = false;
      xHome = false;
      yHome = false;
      isStopped = false;
    }

    while (scanning && !stopMove){ // Scanning commands
        
      for(int z=0; z<NumZPoints && !stopMove; z++){
        if (z%2 == 0){ dirX = LOW;} // alternate movement direction
        else{dirX = HIGH;}

        for (int x = 0; x < NumXPoints && !stopMove; x++) {
          checkStopCommand();
          if (stopMove) break;

            // alternate Y direction
            dirY = yScanDirFlag? HIGH: LOW;
    
            digitalWrite(yDir, dirY);
            for (int y = 0; y < NumYPoints - 1 && !stopMove; y++) {
              // Move Y by one increment
              for (int s = 0; s < stepsPerIncrement; s++) {
                digitalWrite(yStep, HIGH);
                delayMicroseconds(halfDelay);
                digitalWrite(yStep, LOW);
                delayMicroseconds(halfDelay);
                checkStopCommand(); if (stopMove) break;
              }
            }

            yScanDirFlag = !yScanDirFlag;
            // After finishing a Y pass, step +X one increment
            if (x < NumXPoints - 1 && !stopMove) {
              digitalWrite(xDirRight, dirX);
              digitalWrite(xDirLeft, dirX);
              for (int s = 0; s < stepsPerIncrement; s++) {
                digitalWrite(xStepRight, HIGH);
                digitalWrite(xStepLeft, HIGH);
                delayMicroseconds(halfDelay);
                digitalWrite(xStepRight, LOW);
                digitalWrite(xStepLeft, LOW);
                delayMicroseconds(halfDelay);
                checkStopCommand(); if (stopMove) break;
              }
            }
        }
          digitalWrite(zDir, HIGH);
          for (int s=0; s<stepsPerIncrement && !stopMove; s++){
            digitalWrite(zStep, HIGH);
            delayMicroseconds(halfDelay);
            digitalWrite(zStep, LOW);
            delayMicroseconds(halfDelay);
            checkStopCommand(); if (stopMove) break;
          }
      }

    delayMicroseconds(halfDelay);
    if (stopMove) {Serial.println("Scan Stopped!");} 
    else {Serial.println("Completed!");}
    scanning = false;
    }
  }

//create a duty cycle for stepping in the X direction 
//CW or CCW is determined above based on cmd read at port
//only on the rising edge triggers a step 
  checkXSwitches();
  checkYSwitches();

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
    digitalWrite(yDir, dirY);
    digitalWrite(yStep, HIGH);
    delayMicroseconds(halfDelay);
    digitalWrite(yStep, LOW);
    delayMicroseconds(halfDelay);
  }

  if (moveZ) {
    digitalWrite(zStep, HIGH);
    delayMicroseconds(halfDelay);
    digitalWrite(zStep, LOW);
    delayMicroseconds(halfDelay);
  } 
}

// Helper Functions:
void checkStopCommand(){
  if (Serial.available()) {
    String newCmd = Serial.readStringUntil('\n');
    newCmd.trim();
    lastCommand = millis();
    if (newCmd == "S-" || newCmd == "H-") {
      stopMove = true;
    }
  }
}

void checkSwitchStatus(){
  int switchStateY1 = digitalRead(limitSwitchY1);
  int switchStateX1 = digitalRead(limitSwitchX1);

  xHome = (switchStateX1 == LOW);
  yHome = (switchStateY1 == LOW);

  isStopped = xHome && yHome;
}

void checkYSwitches(){
  int switchStateY1 = digitalRead(limitSwitchY1);
  int switchStateY2 = digitalRead(limitSwitchY2);
  //HIGH == LEFT & LOW == RIGHT for dirY
  //HIGH == UNTOUCHED & LOW == TOUCHED for switch state

  if (dirY == LOW && switchStateY1 == LOW) {
    moveY = false;
  }

  else if (dirY == HIGH && switchStateY2 == LOW) {
    moveY = false;
  }
}

void checkXSwitches(){
  int switchStateX1 = digitalRead(limitSwitchX1);
  int switchStateX2 = digitalRead(limitSwitchX2);
  //HIGH == FORWARDS & LOW == BACKWARDS for dirX
  //HIGH == UNTOUCHED & LOW == TOUCHED for switch state

  if(dirX == HIGH && switchStateX1 == LOW){
    moveX = false;
  }
  else if (dirX == LOW && switchStateX2 == LOW){
    moveX = false;
  }
}