
//Sends Serial output when a state changes
// Ie every button press we get output for pressed and released
// Format is X[0] where X is key and 0 is value
// Has Digital pin debouncing and threshold value for pot changes
// Button are expected to be ordered toggle, higher, lower in the buttonValues array
//Pin 2-13 A1,A2,A3,A4 Buttin Inputs
int potIn = A0;
bool enabled[] = {false, false,false,false,false};
int sensorValue = 0;
int previousSensor = 0;
int buttonValues[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int previousValues[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int bounceDelay = 5;
int ignorePin[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int threshold = 5;

void setup() {
  for(int i=2;i<14;i++)
  {
    pinMode(i,INPUT);
  }
  
  pinMode(A1,INPUT);
  pinMode(A2,INPUT);
  pinMode(A3,INPUT);
  pinMode(A4,INPUT);

  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int rawSensor = analogRead(potIn);
  sensorValue = map(rawSensor,0,1023,0,254);
  for(int i=2;i<14;i++)
  {
    buttonValues[i-2] = digitalRead(i);
  }
  buttonValues[11] = digitalRead(A1);
  buttonValues[12] = digitalRead(A2);
  buttonValues[13] = digitalRead(A3);
  buttonValues[14] = digitalRead(A4);

  bool stateChanged = false;
  if(abs(sensorValue - previousSensor)>threshold){
    processsChange(-1);
    previousSensor = sensorValue;
  }
  for(int i=0;i<15;i++){
    if(ignorePin[i]<=0){
      if(previousValues[i] != buttonValues[i]){
        processsChange(i);
        previousValues[i] = buttonValues[i];
        ignorePin[i] = bounceDelay;
    }
    }else{
      ignorePin[i]--;
    }
    
  }
  

  delay(10);

}

//Print changed to Serial
void SendUpdate(char key, int value){
  Serial.print(key);
  Serial.print("[");
  Serial.print(value);
  Serial.println("]");
}

//Logic to control what is printed to Serial and how array is layed out
void processsChange(int index)
{
  int remainder = index % 3;
  if(index == -1)
  {
    SendUpdate('T',sensorValue);
  }else if(remainder == 0){
    int buttonIndex = index/3;
    if(enabled[buttonIndex]){
      SendUpdate('D',buttonIndex);
      enabled[buttonIndex] = false;
    }else{
      SendUpdate('E',buttonIndex);
      enabled[buttonIndex] = true;
    }
  }else if(remainder == 1)
  {
    if(buttonValues[index]==1){
      int controlIndex = index/3;
      SendUpdate('H',controlIndex);
    }
  }else if (remainder == 2){
    if(buttonValues[index]==1){
      int controlIndex = index/3;
      SendUpdate('L',controlIndex);
    }
  }
}
