#include <AFMotor.h>                                                          
#include <DS1307RTC.h>
#include <Wire.h>
#include <Time.h>
#define enc_clk A3
#define enc_dt A2

int dir=1;                                                                             // set direction (1=FORWARD WITH CORRECTIONS [tracking]; 2=BACKWARD; 3=FORWARD CALIBRATE)

// MOTOR PARAMETERS

int nsteps=48;                                                                         // number of steps per motor rotation (48 = 7.5 deg/step)
int nmotor=2;                                                                          // board motor controller number
int shaft_rot=8;                                                                       // RA worm rotation rate (min/rotation) for siderial tracking
int gear_ratio=200;                                                                    // gear ratio of motor                                  
//double slew=1.0042;                                                                    // speed up for slewing (1 = nominal siderial).  Adjust for slow motor
double slew=1.00;
double srpm=slew*gear_ratio/shaft_rot;                                                 // rpm for siderial tracking
double rpm;                                                                            // adjusted rpm
double rrpm;                                                                           // rounded rpm+rem
double rem;                                                                            // fractional numbers of steps left after rounding
int n=20;                                                                              // number of steps per run of motor at 25 rpm
int m;                                                                                 // number of steps per run of motor

// TIME PARAMETERS

tmElements_t tm;                                                                       // time elememts read from RTC
tmElements_t tc;                                                                       // time elements read from computer
time_t t0;                                                                             // start time
int t;                                                                                 // time

// ROTARY ENCODER PARAMETERS

int rot_steps=80;                                                                      // number of steps in rotary encoder
int clk;                                                                               // pin A digital value
int dt;                                                                                // pin B digital value
int phase;                                                                             // phase (rotary encoder step)
int oldphase;                                                                          // phase at previous measurement
int totphase=0;                                                                        // accumulated phase

// CALIBRATION PARAMETERS

const int ncal=960;                                                                    // number of calibration loops
int toff=-80;                                                                            // calibration solution time offset
float r;                                                                               // linear rate
float a;                                                                               // amplitude of first sinusoid
float b;                                                                               // angular frequency of first sinusoid
float c;                                                                               // phase offset of first sinusoid
float d;                                                                               // amplitude of second sinusoid
float e;                                                                               // angular frequency of second sinusoid
float f;                                                                               // phase offset of second sinusoid
float g;                                                                               // amplitude of third sinusoid
float h;                                                                               // angular frequency of third sinusoid
float k;                                                                               // phase offset of third sinusoid

// LOOP COUNTERS

int i;                                                                                 // loop counter

AF_Stepper motor(nsteps,nmotor);                                                       // set up motor

void setup() {                                                                         // initial calibration
  Serial.begin(9600);                                                                  // set up Serial library at 9600 bps  
  pinMode(enc_clk, INPUT_PULLUP);                                                      // pin for rotary encoder pin A
  pinMode(enc_dt, INPUT_PULLUP);                                                       // pin for rotary encoder pin B
  motor.setSpeed(srpm);                                                                // set motor speed
  Serial.setTimeout(10000);                                                            // set serial timeout to 10 seconds

  while (!Serial.available());                                                         // wait until bytes available to read
  
  if (Serial.available()>0) {
    tc.Year=Serial.parseInt();                                                         // read year from computer
    tc.Month=Serial.parseInt();                                                        // read month from computer
    tc.Day=Serial.parseInt();                                                          // read day from computer
    tc.Hour=Serial.parseInt();                                                         // read hour from computer
    tc.Minute=Serial.parseInt();                                                       // read minute from computer
    tc.Second=Serial.parseInt();                                                       // read second from computer
    RTC.write(tc);                                                                     // adjust time on RTC to computer time
  }

  Serial.print(tc.Year+1970);                                                          // print time back to check
  Serial.print(" ");
  Serial.print(tc.Month);
  Serial.print(" ");
  Serial.print(tc.Day);
  Serial.print(" ");
  Serial.print(tc.Hour);                                                           
  Serial.print(" ");
  Serial.print(tc.Minute);
  Serial.print(" ");
  Serial.print(tc.Second);
  Serial.print("\n");

  Serial.print(ncal);                                                                  // tell python how many calibration loops to expect
  Serial.print("\n");

  if (RTC.read(tm)) {
    t0=makeTime(tm);                                                                   // get start time
    Serial.print(t0);
    Serial.print("\n");
    clk=digitalRead(enc_clk);                                                          // get pin A value
    dt=digitalRead(enc_dt);                                                            // get pin B value
    if (clk==0 && dt==0) {                                                             // calculate phase
      phase=1;
    }
    if (clk==0 && dt==1) {
      phase=2;
    }
    if (clk==1 && dt==1) {
      phase=3;
    }
    if (clk==1 && dt==0) {
      phase=4;
    }
    t=0;
    Serial.print(t);                                                                  // print time and phase
    Serial.print(" ");
    Serial.print(0);
    Serial.print(" ");
    Serial.print(clk);                                                                  // print time and phase
    Serial.print(" ");
    Serial.print(dt);    
    Serial.print("\n");
  } else {
    if (RTC.chipPresent()) {
      Serial.println("The DS1307 is stopped.  Please run the SetTime");
      Serial.println("example to initialize the time and begin running.");
      Serial.println();
    } else {
      Serial.println("DS1307 read error!  Please check the circuitry.");
      Serial.println();
    }
  }

  motor.step(n, FORWARD, SINGLE);                                                      // run motor at siderial rate
  rem=srpm-round(srpm);                                                                // remainder for constant drive rate
  
  for (i=1;i<ncal+1;i++) {
    if (RTC.read(tm)) {
      t=makeTime(tm)-t0;                                                               // calculate time from t0
      clk=digitalRead(enc_clk);                                                        // get pin A value
      dt=digitalRead(enc_dt);                                                          // get pin B value
      oldphase=phase;                                                                  // save current phase to compare with new phase
      if (clk==0 && dt==0) {                                                           // calculate phase
        phase=1;
      }
      if (clk==0 && dt==1) {
        phase=2;
      }
      if (clk==1 && dt==1) {
        phase=3;
      }
      if (clk==1 && dt==0) {
        phase=4;
      }
      if (phase==oldphase) {                                                           // if phase unchanged don't accumulate phase
        phase=oldphase;
      }
      if (phase==oldphase+1 || phase==oldphase-3) {                                    // if phase increments, accumulate it
        totphase=totphase+1;
      }
      Serial.print(t);                                                                 // print time and phase
      Serial.print(" ");
      Serial.print(totphase);
      Serial.print(" ");
      Serial.print(clk);                                                                  
      Serial.print(" ");
      Serial.print(dt); 
      Serial.print(" ");
      Serial.print(rem); 
      Serial.print(" ");
      Serial.print(rrpm);
      Serial.print("\n");
    } else {
      if (RTC.chipPresent()) {
        Serial.println("The DS1307 is stopped.  Please run the SetTime");
        Serial.println("example to initialize the time and begin running.");
        Serial.println();
      } else {
        Serial.println("DS1307 read error!  Please check the circuitry.");
        Serial.println();
      }
    }
    rrpm=round(srpm+rem);                                                              // rounded rpm+rem
    motor.setSpeed(rrpm);                                                              // set motor speed
    m=round(n*(srpm+rem)/srpm);                                                        // calculate how many steps
    motor.step(m, FORWARD, SINGLE);                                                    // run motor forward
    rem=srpm+rem-rrpm;                                                                 // calculate remainder to carry forward to next period
  }
  if (Serial.available()>0) {                                                          // get the coefficients for the drive correction
    r=Serial.parseFloat();
    a=Serial.parseFloat();
    b=Serial.parseFloat();
    c=Serial.parseFloat();
    d=Serial.parseFloat();
    Serial.print(r,4);                                                                 // print time and phase
    Serial.print(" ");
    Serial.print(a,4);
    Serial.print(" ");
    Serial.print(b,4);                                                                  
    Serial.print(" ");
    Serial.print(c,4); 
    Serial.print(" ");
    Serial.print(d,4);
    Serial.print("\n");
  }
  if (Serial.available()>0) {
    e=Serial.parseFloat();
    f=Serial.parseFloat();
    g=Serial.parseFloat();
    h=Serial.parseFloat();
    k=Serial.parseFloat();
    Serial.print(e,4);
    Serial.print(" ");
    Serial.print(f,4);
    Serial.print(" ");
    Serial.print(g,4);
    Serial.print(" ");
    Serial.print(h,4);
    Serial.print(" ");
    Serial.print(k,4);
    Serial.print("\n");
  }
  rem=0;
}

void loop() {
  if (RTC.read(tm)) {
    t=makeTime(tm)-t0;
    clk=digitalRead(enc_clk);                                                        // get pin A value
    dt=digitalRead(enc_dt);                                                          // get pin B value
    oldphase=phase;                                                                  // save current phase to compare with new phase
    if (clk==0 && dt==0) {                                                           // calculate phase
      phase=1;
    }
    if (clk==0 && dt==1) {
      phase=2;
    }
    if (clk==1 && dt==1) {
      phase=3;
    }
    if (clk==1 && dt==0) {
      phase=4;
    }
    if (phase==oldphase) {                                                           // if phase unchanged don't accumulate phase
      phase=oldphase;
    }
    if (phase==oldphase+1 || phase==oldphase-3) {                                    // if phase increments, accumulate it
      totphase=totphase+1;
    }
  } else {
    if (RTC.chipPresent()) {
      Serial.println("The DS1307 is stopped.  Please run the SetTime");
      Serial.println("example to initialize the time and begin running.");
      Serial.println();
    } else {
      Serial.println("DS1307 read error!  Please check the circuitry.");
      Serial.println();
    }
  }
  if (dir==1) {  
    rpm=srpm+60*gear_ratio*a*b*cos(b*(t+toff)+c)/rot_steps+60*gear_ratio*d*e*cos(e*(t+toff)+f)/rot_steps+0.5*60*gear_ratio*g*h*cos(h*(t+toff)+k)/rot_steps;   // adjust speed with calibration parameters
    rrpm=round(rpm+rem);                                                               // rounded rpm+rem
    Serial.print(t);                                                                   // print time and phase
    Serial.print(" ");
    Serial.print(totphase);
    Serial.print(" ");
    Serial.print(clk);                                                                  
    Serial.print(" ");
    Serial.print(dt); 
    Serial.print(" ");
    Serial.print(rpm);                                                                  
    Serial.print(" ");
    Serial.print(rem); 
    Serial.print(" ");
    Serial.print(rrpm);
    Serial.print("\n");
    motor.setSpeed(rrpm);                                                              // set motor speed
    m=round(n*rpm/srpm);                                                               // calculate how many steps
    motor.step(m, FORWARD, SINGLE);                                                    // run motor forward
    rem=rpm+rem-rrpm;                                                                  // calculate remainder to carry forward to next period
  }
  if (dir==2) {
    rrpm=round(srpm+rem);                                                              // rounded rpm+rem
    motor.setSpeed(rrpm);                                                              // set motor speed
    motor.step(n, BACKWARD, SINGLE);                                                   // run motor backward
    rem=srpm+rem-rrpm;                                                                 // calculate remainder to carry forward to next period
  }
  if (dir==3) {
    rrpm=round(srpm+rem);                                                              // rounded rpm+rem
    motor.setSpeed(rrpm);                                                              // set motor speed
    motor.step(n, FORWARD, SINGLE);                                                    // run motor forward
    rem=srpm+rem-rrpm;                                                                 // calculate remainder to carry forward to next period
  }
}
