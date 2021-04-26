#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 13:11:47 2021

@author: stingay
"""

import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime
import time

# Set up arrays

t=np.array([])
p=np.array([])
tm=np.array([])
rpm=np.array([])

# Calibration function for fitting rotary encoder data

def funcp(xx, a, b, c, e, f, h, aa, cc):
    return a*xx + b + c*np.sin(0.0131*xx+e) + f*np.sin(0.0262*xx+h) + aa*np.sin(0.0524*xx+cc)

# Open serial port (also restarts sketch): you need to determine which serial port is being used and edit the next line of code

ser=serial.Serial('/dev/cu.usbmodem141101')
print(ser.name)

# Flush serial buffers

ser.flushInput()
ser.flushOutput()

# Sleep until sketch restarted

print("Sleeping for 20 seconds to allow the Arduino board to boot")
time.sleep(20)

# Get computer time

now=datetime.now()
YY=now.year-1970
MM=now.month
DD=now.day
hh=now.hour
mm=now.minute
ss=now.second

# Send computer time to arduino RTC

ser.write(bytes(str(YY)+".",'utf-8'))
ser.write(bytes(str(MM)+".",'utf-8'))
ser.write(bytes(str(DD)+".",'utf-8'))
ser.write(bytes(str(hh)+".",'utf-8'))
ser.write(bytes(str(mm)+".",'utf-8'))
ser.write(bytes(str(ss)+" ",'utf-8'))

# Read computer time back from arduino RTC to check

text=str(ser.readline())
newtext=text.replace("b'","").replace("\\n'","")
print(now,newtext)

# Get number of calibration loops

text=str(ser.readline())
newtext=text.replace("b'","").replace("\\n'","")
n=int(newtext)
print(n)

# Read setup calibration loop

text=str(ser.readline())
t0=text.replace("b'","").replace("\\n'","")

# Open file to write rotary encoder calibration data

f=open("steps-v-time-0425-3.txt","w")
f.write("{}\n".format(t0))

# Read rotary encoder calibration data

i=0
while i<n+1:
    text=str(ser.readline())
    newtext=text.replace("b'","").replace("\\n'","")
    array=np.array(newtext.split(" "))
    t=np.append(t,float(array[0]))
    p=np.append(p,float(array[1]))
    print(newtext)
    f.write("{} {}\n".format(t[i],p[i]))
    i=i+1

f.close()

# Fit the calibration function (and round off to send to arduino as floats)

poptp, pcovp = curve_fit(funcp, t, p, (0.166,0,0.4,0,0.1,0,0.05,0))
r=int(10000*poptp[0]+0.5)/10000
a=int(10000*poptp[2]+0.5)/10000
b=0.0131
c=int(10000*poptp[3]+0.5)/10000
d=int(10000*poptp[4]+0.5)/10000
e=0.0262
f=int(10000*poptp[5]+0.5)/10000
g=int(10000*poptp[6]+0.5)/10000
h=0.0524
k=int(10000*poptp[7]+0.5)/10000

print(r,a,b,c,d,e,f,g,h,k)

# Send the calibration coefficients to arduino

ser.write(bytes(str(r)+" ",'utf-8'))
ser.write(bytes(str(a)+" ",'utf-8'))
ser.write(bytes(str(b)+" ",'utf-8'))
ser.write(bytes(str(c)+" ",'utf-8'))
ser.write(bytes(str(d)+" ",'utf-8'))

# Read back first five coefficients

text=str(ser.readline())
newtext=text.replace("b'","").replace("\\n'","")
print(newtext)

ser.write(bytes(str(e)+" ",'utf-8'))
ser.write(bytes(str(f)+" ",'utf-8'))
ser.write(bytes(str(g)+" ",'utf-8'))
ser.write(bytes(str(h)+" ",'utf-8'))
ser.write(bytes(str(k)+" ",'utf-8'))

# Read back second five coefficients

text=str(ser.readline())
newtext=text.replace("b'","").replace("\\n'","")
print(newtext)

# Open file to write rotary encoder data after calibration

f=open("steps-v-time-cal-0425-3.txt","w")
f.write("{}\n".format(t0))

# Read rotary encoder data

i=0
while i<480:
    text=str(ser.readline())
    newtext=text.replace("b'","").replace("\\n'","")
    array=np.array(newtext.split(" "))
    t=np.append(t,float(array[0]))
    p=np.append(p,float(array[1]))
    print(newtext)
    f.write("{} {}\n".format(float(array[0]),float(array[1])))
    i=i+1

f.close()

# Plot the calibration data, the fit, and the residuals

plt.figure()
plt.plot(t, funcp(t, *poptp)-p)
plt.plot(t, p-poptp[0]*t-poptp[1])
plt.plot(t, funcp(t, *poptp)-poptp[0]*t-poptp[1])
plt.xlabel("Time (s)")
plt.ylabel("Phase (steps)")

# Flush the serial buffers and close the serial port

ser.flushInput()
ser.flushOutput()
ser.close()
