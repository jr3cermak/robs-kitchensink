/*
Davis Instruments DS7911 Anemometer

In this circuit, we will sample the wind direction and wind speed from the
Davis Instruments DS7911 Anemometer every 5 seconds.  Referenced code adds more
features such as saving/recalling calibration to available EEPROM.  These
sketches utilize the Serial output for information display.  Feel free to get
creative and use a LCD instead!

The PDF documentation for the DS7911 has the Red wire to Ground.  Be aware
of the wire mapping.

The millis() will eventually wrap around if the sketch is running for a long
period of time.  There will be an odd reading when this happens as a result
of the sample time span going negative for one sample.  We will also drop a
pulse.  See the interrupt function.

Experiment on ways you can improve this code and/or integrate with
other sensors!  Do your other sensors need interrupts?  Will turning
off/on all the interrupts cause trouble with your other sensors that need
them?  Welcome to the race and meet our friend race conditions!

Parts
  (1)  KIT-12001          : SparkFun             : SparkFun Inventor's Kit V3 https://www.sparkfun.com/products/12001
  (2)  DS7911             : Davis Instruments    : http://www.davisnet.com/product_documents/weather/spec_sheets/7911_SS.pdf
  (3)  Arduino IDE        : Arduino              : http://arduino.cc/en/Main/Software
                                                   http://www.arduino.cc  
References
  (1)
    Comparison : https://learn.sparkfun.com/tutorials/redboard-vs-uno/all
    Vital data : ATmega328
  (2)
    Manual     : http://www.davisnet.com/product_documents/weather/spec_sheets/7911_SS.pdf (2/26/2013: Davis Instruments, Rev. G)
    Wiring     : https://code.google.com/p/arduwind/downloads/list (May 2011, Jan 2012: Thierry Brunet de Courssou)
    Wiring     : http://www.emesystems.com/OL2wind.htm (2007: Electronically Monitored Systems)
    Code       : https://code.google.com/p/arduwind/source/browse/trunk/ArduWind.ino 
                 (May 2011, Jan 2012: Thierry Brunet de Courssou)
    Code       : http://www.qsl.net/on7eq/projects/arduino_davis.htm (Jan 2012: Jean-Jacques DE REY; ON7EQ)
  (3):
    Interrupts :
      http://arduino.cc/en/Reference/AttachInterrupt
        Explains interrupt to digital pin mapping
    Internal pull up resistor:
      http://arduino.cc/en/Reference/Constants
        Used to silence noise on the wind speed contact closure to ground
        signal.  Also borrowed debounce code.

Requirements

  This sketch requires the use of an interrupt.  On the Arduino Uno,
  this limits access to GPIO 2 and 3 for interrupts 0 and 1.  See
  AttachInterrupts link above for pin assignments on various boards.
  
  Do not apply a direct power source to the wind instrument.  This
  may damage it.   Use the low power sources from the Arduino.
      
Hardware Connections

  DS7911
  
    Black  : Wind speed contact closure to ground
    Red    : Ground
    Green  : Wind direction pot wiper (20K ohms potentiometer)
    Yellow : Pot supply voltage

  DS7911 to Breadboard
  
    Yellow  to j27
    Green   to j28
    Red     to j29
    Black   to j30

  RedBoard to Breadboard
  
    +5V     to BB+
    GND     to BB-
    BB+     to f27
    A0      to f28
    BB-     to f29
    GPIO2   to f30

Changes
  20140308: 1.1 clean up and put into a tutorial like format
  20140308: 1.0 initial version

This sketch was written by Rob Cermak,
with lots of help from the Arduino community
and adapted from sketches and other information
published on the internet.

This code is completely free for any use.

Version 1.1 20140308 JRC  
*/

// Define PINs before setup()

int WindSpeedInterrupt = 0;         // Uno: Interrupt 0 = GPIO 2
int WindSpeedPin = 2;               // GPIO 2 = Interrupt 0
int WindDirectionAnalogPin = 0;     // A0

// Define storage variables

// Special variables for the interrupt function
// One to tally the pulses and one used as a timeout
// to debounce the reed switch.
volatile long windspeedcounter = 0;
volatile long ContactTime = 0; 

// Variables to compute the wind speed and
// wind direction.  We will copy data into
// them before performing calculations.
int winddirectioninputvalue = 0;
int winddirection = 0;
long windspeedct = 0;
long lastreadspeed = millis();
long elapsedtime = 0;
long timenow = 0;
float windspeed = 0.0;

void setup()
{
  // Set up GPIO (digital pin) for INPUT with the internal pull up
  // resistor to help quiet the noise on the digital signal 
  pinMode(WindSpeedPin, INPUT_PULLUP);
  
  // Initialize Serial output to display information
  Serial.begin(9600);
  Serial.println("------>");

  // End of setup, initialize final variables going
  // into the main loop()
  
  // Seed the debounce timer with current time
  ContactTime = millis();

  // Connect the interrupt up to the function that
  // counds the wind speed switch closure pulses.  We
  // choose FALLING as the signal is pulled up HIGH
  // with the pull up resistor.  When the switch is
  // closed, the signal is pulled down.
  attachInterrupt(WindSpeedInterrupt, WindSpeedCounter, FALLING);
  lastreadspeed = millis();
  
}

void loop()
{
  // Wait 5 seconds to collect data
  delay(5000);

  // Read Wind Direction from Analog Pin
  // We use the Arduino math operation map to turn the
  // analog signal from 0 to 1023 and linearly map it to
  // the degree range of 0 to 359.  As the wind vane turns
  // the resistance is varied.  Fortunately, it is a linear
  // response.
  // Using a 5V signal:
  //   North ~ 0V   or 0    or 0   degrees
  //   South ~ 2.5V or 512  or 180 degrees
  winddirectioninputvalue = analogRead(WindDirectionAnalogPin);
  winddirection = map(winddirectioninputvalue, 0, 1023, 0, 359);

  // Read Wind Speed
  //   Computed from accumulated pulses and elapsed time
  //   Wind Speed (mph) = Pulses * (2.25 / Elapsed time in Seconds)
  
  // We turn interrupts off to capture the number of pulses
  // in the time interval.  We temporarily store this
  // for calculation later.  We clear the variable and turn
  // the interrupts back on to capture more data.   We also
  // calcuate the time span between readings and update the
  // time keeping variable (lastreadspeed).
  // Do we lose data while we have the interrupts off? Yes!
  // If we don't turn the interrupts off, we may get an additional
  // pulse or so in our calculation! 
  // It also takes time to capture the data as well.  We
  // assume here that things are moving quickly enough to be
  // as accurate as possible.
  
  // Turn interrupts off
  noInterrupts();

  // Get the elapsed time and update the time keeping 
  // variable
  timenow = millis();
  elapsedtime = timenow - lastreadspeed;
  lastreadspeed = millis();

  // Get a copy of the number of pulses and zero
  // out the counter
  windspeedct = windspeedcounter;
  windspeedcounter = 0;
  
  // Turn interrupts back on -- collect data!
  interrupts();
 
  // Display the number of pulses we collected 
  Serial.print("Pulses:");
  Serial.print(windspeedct);

  // Display elapsed time between samples
  // I've noted about 1 to 2 ms is needed to
  // collect data.  Elapsed time is around 5001
  // or 5002 ms.
  Serial.print(" Elapsed Time(ms):");
  Serial.print(" ");
  Serial.print(elapsedtime);
  
  // Compute the wind speed using the formula from
  // the sensor manual
  windspeed = windspeedct * (2.25 / (elapsedtime / 1000.0));

  // Display the wind speed
  Serial.print(" Spd (mph):");
  Serial.print(windspeed);
  
  // Display the wind direction  
  Serial.print(" Dir (Deg):");    
  Serial.println(winddirection);
}

// This function is called an Interrupt Service Routine (ISR),
// it is run each time the interrupt occurs.
// It is a very good idea to keep this small and
// compact so the routine runs very fast to allow
// control to go back to the main loop().

// Collect wind speed pulses from the anemometer
void WindSpeedCounter()
{
  // Debounce code: If we see a signal that is faster than 15ms 
  // per pulse, ignore it.  NOTE: if this program runs for a long
  // period of time, a pulse will be dropped when millis() time
  // wraps around.
  
  // 15 ms allows for capture of wind up to 150 kph (93.2 mph).
  if ((millis() - ContactTime) > 15 ) {
    windspeedcounter++;
    ContactTime = millis();
  }
}
