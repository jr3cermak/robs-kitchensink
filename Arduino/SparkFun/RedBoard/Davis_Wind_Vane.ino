/**
  * SparkFun RedBoard (ala Arduino Uno)
  * Notes:
  *   The instrument was prototyped on a Sparkfun RedBoard.  More documentation needs to be
  *   added to turn this into a full tutorial.  The target platform is the pcDuino V2.
  *
  * Sketch Author     : Rob Cermak
  * Last Updated      : 2014-03-08
  * Instrument(s) :
  *   (1) Davis Instruments DS7911
  * REFERENCES:
  *   (1):
  *     Interrupts : http://arduino.cc/en/Reference/AttachInterrupt
  *     Manual     : http://www.davisnet.com/product_documents/weather/spec_sheets/7911_SS.pdf (2/26/2013: Davis Instruments, Rev. G)
  *     Wiring     : https://code.google.com/p/arduwind/downloads/list (May 2011, Jan 2012: Thierry Brunet de Courssou)
  *     Wiring     : http://www.emesystems.com/OL2wind.htm 
  *     Code       : https://code.google.com/p/arduwind/source/browse/trunk/ArduWind.ino 
  *                  (May 2011, Jan 2012: Thierry Brunet de Courssou)
  *     Code       : http://www.qsl.net/on7eq/projects/arduino_davis.htm (Jan 2012: Jean-Jacques DE REY; ON7EQ)
  *
  * SparkFun Inventors Kit Breadboard Circuit Layout
  *   GPIO 2 = Interrupt 0 = WindSpeed 
  * 
  * 
  */

int WindSpeedInterrupt = 0;         // Interrupt 0 = GPIO 2 (Uno)
int WindSpeedPin = 2;               // GPIO2 = Int 0
int WindDirectionAnalogPin = 0;     // A0
int winddirectioninputvalue = 0;
int winddirection = 0;
volatile long windspeedcounter = 0;
long windspeedct = 0;
volatile long ContactTime = millis(); 
int oldct = 0;
long lastreadspeed = millis();
long elapsedtime = 0;
long timenow = 0;
float windspeed = 0.0;

void setup()
{
  pinMode(WindSpeedPin, INPUT_PULLUP);
  attachInterrupt(WindSpeedInterrupt, WindSpeedCounter, FALLING);
  
  // Serial debugging for now
  Serial.begin(9600);
  Serial.println("------>");
}

void loop()
{
  // Read Direction
  winddirectioninputvalue = analogRead(WindDirectionAnalogPin);
  winddirection = map(winddirectioninputvalue, 0, 1023, 0, 359);
  Serial.print("Count:");
  Serial.print(windspeedcounter);
  
  // Read Wind Speed
  
  // Turn interrupts off just to grab a data sample and then turn
  // interrupts back on to collect while we finish reporting.
  noInterrupts();
  timenow = millis();
  elapsedtime = timenow - lastreadspeed;
  windspeedct = windspeedcounter;
  windspeedcounter = 0;
  lastreadspeed = millis();
  interrupts();
  
  Serial.print(" Spd:");
  windspeed = windspeedct * (2.25 / (elapsedtime / 1000.0));
  Serial.print(windspeed);
  
  Serial.print(" [");
  Serial.print(windspeedct);
  Serial.print(" ");
  Serial.print(elapsedtime);
  Serial.print("]");
  
  Serial.print(" Dir:");    
  Serial.println(winddirection);
  delay(5000);
}

// Interrupt routine -- keep simple & fast
void WindSpeedCounter()
{
  // Debounce code; does not seem to be needed with the INPUT_PULLUP
  // 15 ms allows for capture of wind up to 150 kph (93.2 mph).  Instrument
  if ((millis() - ContactTime) > 15 ) {
    windspeedcounter++;
    ContactTime = millis();
  }
}
