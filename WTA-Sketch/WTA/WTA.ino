
//Sends Serial output when a state changes
// Ie every button press we get output for pressed and released
// Format is T[0],E[0],D[0],H[0],L[0]
// Has Digital pin debouncing and threshold value for pot changes


int button1 = 2;
int button2 = 3;
int button3 = 4;
int button4 = 5;
int potIn = A0;


int values[] = {0,0,0,0,0};
int previousValues[] = {0,0,0,0,0};
int bounceDelay = 5;
int ignorePin[] = {0,0,0,0,0};
int threshold = 5;

void setup() {
  pinMode(button1,INPUT);
  pinMode(button2,INPUT);
  pinMode(button3,INPUT);
  pinMode(button4,INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int rawSensor = analogRead(potIn);
  values[0] = map(rawSensor,0,1023,0,254);
  values[1] = digitalRead(button1);
  values[2] = digitalRead(button2);
  values[3] = digitalRead(button3);
  values[4] = digitalRead(button4);

  bool stateChanged = false;
  if(abs(values[0] - previousValues[0])>threshold){
    stateChanged = true;
    previousValues[0] = values[0];
  }
  for(int i=1;i<5;i++){
    if(ignorePin[i]<=0){
      if(previousValues[i] != values[i]){
        stateChanged = true;
        previousValues[i] = values[i];
        ignorePin[i] = bounceDelay;
    }
    }else{
      ignorePin[i]--;
    }
    
  }

  if(stateChanged){
    SendOutput();
  }
  

  delay(10);

}
//Print output correctly formatted
void SendOutput()
{
  Serial.print("T[");
  Serial.print(values[0]);
  Serial.print("],E[");
  Serial.print(values[1]);
  Serial.print("],D[");
  Serial.print(values[2]);
  Serial.print("],H[");
  Serial.print(values[3]);
  Serial.print("],L[");
  Serial.print(values[4]);
  Serial.print("]\n");
}
