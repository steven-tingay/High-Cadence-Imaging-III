#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 11:24:13 2021

@author: stingay
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime, timezone, timedelta
from collections import deque

def funcxi(xx, a, b):
    return a*xx + b

def funcyi(xx, a, b, c, d, e, f, g, h, aa, bb, cc):
    return a*xx + b + c*np.sin(d*xx+e) + f*np.sin(g*xx+h) + aa*np.sin(bb*xx+cc)

def funcp(xx, a, b, c, e, f, h, aa, cc):
    return a*xx + b + c*np.sin(0.0131*xx+e) + f*np.sin(0.0262*xx+h) + aa*np.sin(0.0524*xx+cc)

x=np.array([])
y=np.array([])
xi=np.array([])
yi=np.array([])
ts=np.array([])
ti=np.array([])
ys=np.array([])
xcl=np.array([])
xclt=np.array([])
tint=5
fac=(1/(80*180))*360*60*60

# choose an appropriate reference date and time for t=0
refdate=datetime(2021,4,25,21,18,00)

# read in all the rotary encoder data
f=open("steps-v-time-0425-3.txt","r")
lines=f.readlines()
dateobs=datetime.fromtimestamp(int(lines[0]))
dateobs=dateobs-timedelta(hours=8)
print(dateobs)
secobs=(dateobs-refdate).seconds
for nline in range(1,len(lines)-1):
    ts=np.append(ts,(dateobs+timedelta(seconds=float(lines[nline].split()[0]))-refdate).seconds)
    ys=np.append(ys,-1*float(lines[nline].split()[1]))
f.close()

# read in all the data from images
g=open("2021-04-25-test3.txt","r")
lines=g.readlines()
dateobi=datetime.strptime(lines[0].strip("\n"), '%Y-%m-%d %H:%M:%S')
print(dateobi)
secobi=(dateobi-refdate).seconds
for nline in range(1,len(lines)-1):
    ti=np.append(ti,(dateobi+timedelta(seconds=tint*nline)-refdate).seconds)
    yi=np.append(yi,float(lines[nline].split()[0]))
    xi=np.append(xi,float(lines[nline].split()[1]))
g.close()

# starting guesses for curve fitting
vxi=(xi[len(xi)-1]-xi[0])/(len(ti)*tint)
cxi=xi[0]

# starting guesses for curve fitting
vyi=(yi[len(yi)-1]-yi[0])/(len(ti)*tint)
cyi=yi[0]
gi=40
hi=0.013
ki=1.3
si=gi/3
vi=4*hi
wi=ki-7.7
aayi=gi/6
bbyi=2*hi
ccyi=ki-7

# fit x and y motions on images as functions of time, as in the defined function (assuming 480 seconds of data)
poptxi, pcovxi = curve_fit(funcxi, ti[0:192], xi[0:192], (vxi,cxi))
poptyi, pcovyi = curve_fit(funcyi, ti[0:192], yi[0:192], (vyi,cyi,gi,hi,ki,si,vi,wi,aayi,bbyi,ccyi))
print(poptyi)
print(poptxi)

# fit the rotary encoder data
poptpi, pcovpi = curve_fit(funcp, ts, ys, (0.166,0,0.4,0,0.1,0,0.05,0))
print(poptpi)

# fit the corrected portion of the x,y image data for a linear function
poptyic,pcovyic=curve_fit(funcxi,ti[193:383],yi[193:383])
print(poptyic)
print(np.std(yi[193:383]-funcxi(ti[193:383],*poptyic)))

# chose the fraction of the amplitude of the sinusoid with quarter the worm period you want to apply in the corrections
ar=1

# find the offset between rotary encoder model and image data model
xct=np.array(range(0,1000))
for i in range(0,500):
    xci=funcyi(xct+i,*poptyi)
    xcs=funcp(xct,poptpi[0],poptpi[1],poptpi[2],poptpi[3],poptpi[4],poptpi[5],ar*poptpi[6],poptpi[7])-poptpi[0]*xct-poptpi[1]
    xc=np.correlate(xci,xcs)
    xcl=np.append(xcl,xc[0])
    xclt=np.append(xclt,i)
max=np.argmax(xcl)
print("Delay between fitted functions =",max, "s")

# make various diagnostic plots (you will have to figure out what they do for yourself) - all for development and testing purposes
lim=383
plt.figure()
plt.plot(ti[0:lim],xi[0:lim]-np.mean(xi[0:lim]))
plt.plot(ts, fac*(ys-poptpi[0]*ts-poptpi[1])+poptyi[0]*ts+poptyi[1]-np.mean(yi[0:lim]))
plt.plot(ti[0:lim],yi[0:lim]-np.mean(yi[0:lim]),color='black')
plt.plot(ti[0:lim], fac*(funcp(ti[0:lim], poptpi[0],poptpi[1],poptpi[2],poptpi[3],poptpi[4],poptpi[5],ar*poptpi[6],poptpi[7])-poptpi[0]*ti[0:lim]-poptpi[1])+poptyi[0]*ti[0:lim]+poptyi[1]-np.mean(yi[0:lim]))
plt.plot(ti[0:lim], funcxi(ti[0:lim], *poptxi)-np.mean(xi[0:lim]))
plt.plot(ti[0:lim], funcyi(ti[0:lim], *poptyi)-np.mean(yi[0:lim]),color='yellow')
plt.plot(ti[0:lim], funcyi(ti[0:lim], *poptyi)-(fac*(funcp(ti[0:lim]-max, poptpi[0],poptpi[1],poptpi[2],poptpi[3],poptpi[4],poptpi[5],ar*poptpi[6],poptpi[7])-poptpi[0]*(ti[0:lim]-max)-poptpi[1]))+poptyi[0]*ti[0:lim]+poptyi[1]-2*np.mean(yi[0:lim]))
plt.xlabel("Time (s)")
plt.ylabel("Offset from mean location (arcseconds)")
plt.savefig("x-y-time.png")

plt.figure()
plt.plot(xi,yi)
plt.plot(funcxi(ti, *poptxi),funcyi(ti, *poptyi))
plt.plot(funcxi(ti,*poptxi),funcyi(ti,poptyi[0],poptyi[1],poptyi[2],poptyi[3],poptyi[4],0,0,0,0,0,0))
plt.plot(funcxi(ti,*poptxi),funcyi(ti,poptyi[0],poptyi[1],0,0,0,poptyi[5],poptyi[6],poptyi[7],0,0,0))
plt.plot(funcxi(ti,*poptxi),funcyi(ti,poptyi[0],poptyi[1],0,0,0,0,0,0,poptyi[8],poptyi[9],poptyi[10]))
plt.scatter([xi[0]],[yi[0]],color='g',s=50)
plt.scatter([xi[len(xi)-1]],[yi[len(yi)-1]],color='r',s=50)
plt.xlabel("S (arcsec)")
plt.ylabel("E (arcsec)")
plt.savefig("x-y.png")

xl=400
xm=xl+480
diff1=funcyi(xct[xl:xm],*poptyi)-poptyi[0]*xct[xl:xm]-poptyi[1]
diff2=fac*(funcp(xct[xl:xm]-max,poptpi[0],poptpi[1],poptpi[2],poptpi[3],poptpi[4],poptpi[5],ar*poptpi[6],poptpi[7])-poptpi[0]*(xct[xl:xm]-max)-poptpi[1])
data1=yi-poptyi[0]*ti-poptyi[1]
data2=fac*(ys-poptpi[0]*ts-poptpi[1])

plt.figure()
plt.plot(xct[xl:xm],diff1)
plt.plot(xct[xl:xm],diff2)
plt.plot(xct[xl:xm],diff1-diff2)
plt.plot(ts+max,data2)
plt.plot(ti,data1)
plt.plot(xct[xl:xm],[0]*(xm-xl))
plt.xlim(xl,xm)
plt.xlabel("Time (s)")
plt.ylabel("Measured/fitted/residual PE (arcsec)")


plt.figure()
plt.plot(ti[0:lim],yi[0:lim]-np.mean(yi[0:lim]))
plt.plot(ti[0:lim],xi[0:lim]-np.mean(xi[0:lim]))
plt.plot(ti[0:lim], funcxi(ti[0:lim], *poptxi)-np.mean(xi[0:lim]))
plt.plot(ti[0:lim], funcyi(ti[0:lim], *poptyi)-np.mean(yi[0:lim]))
plt.xlabel("Time (s)")
plt.ylabel("Offset from mean location (arcseconds)")

plt.figure()
plt.plot(xi[0:lim],yi[0:lim])
#plt.plot(funcxi(ti[0:lim], *poptxi),funcyi(ti[0:lim], *poptyi))
plt.scatter([xi[0]],[yi[0]],color='g',s=50)
plt.scatter([xi[lim-1]],[yi[lim-1]],color='r',s=50)
plt.xlabel("x-axis sensor position (arcseconds)")
plt.ylabel("y-axis sensor position (arcseconds)")

fac=1
plt.figure()
plt.plot(ts, fac*(ys-poptpi[0]*ts-poptpi[1]))
plt.plot(ti[0:lim], fac*(funcp(ti[0:lim], poptpi[0],poptpi[1],poptpi[2],poptpi[3],poptpi[4],poptpi[5],ar*poptpi[6],poptpi[7])-poptpi[0]*ti[0:lim]-poptpi[1]))
plt.xlabel("Time (s)")
plt.ylabel("Residual phase (encoder steps)")
