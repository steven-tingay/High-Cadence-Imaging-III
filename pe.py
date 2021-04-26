#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 08:20:04 2021

@author: stingay
"""

import numpy as np
from numpy import unravel_index
import os
import exifread
import datetime
import rawpy
import time

x=np.array([])
y=np.array([])
sertime=np.array([])
serphase=np.array([])
dtime=np.array([])
done=[]

# plate scale for the sensor and optical system
pix=1.18

# open a file to write results to
g=open("2021-04-25-test3.txt","w")

# directory containing images
dir='/Users/stingay/Pictures/2021_04_25/'
imglist=sorted(os.listdir(dir))

# open first image and extract jpg thumhail to extract timing information
rawA=rawpy.imread(dir+imglist[0]) # Canon RP
thumb = rawA.extract_thumb()
f=open('thumb.jpg','wb')
f.write(thumb.data)
exif=exifread.process_file(open('thumb.jpg','rb'))
for tag in exif.keys():
    if tag=='Image DateTime':
        datetag=exif[tag]
        date_time=str(datetag).split(' ')
        date=date_time[0].split(':')
        t=date_time[1].split(':')
        dateob=datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(t[0]),int(t[1]),int(t[2]))
        print(dateob)
g.write("{}\n".format(dateob))

# loop over images in directory, detect star in images, and record the coordinate information in the output file
n=0
while len(imglist)>0:
    for img in imglist:
        done.append(img)
        rawA=rawpy.imread(dir+img) # Canon RP
        rgbA = rawA.postprocess(gamma=(1,1), no_auto_bright=True, output_bps=16, bad_pixels_path=None)
        bwA=(rgbA[:,:,0]/np.mean(rgbA[:,:,0])+rgbA[:,:,1]/np.mean(rgbA[:,:,1])+rgbA[:,:,2]/np.mean(rgbA[:,:,2]))/3

        maxind=unravel_index(bwA.argmax(), bwA.shape)
        x=np.append(x,pix*maxind[0])
        y=np.append(y,pix*maxind[1])
        timeob=dateob+datetime.timedelta(seconds=n*5)
        n=n+1
        print(img,maxind[0],maxind[1],timeob)
        g.write("{} {}\n".format(pix*maxind[0],pix*maxind[1]))
    print("Get next lot\n")
    time.sleep(5)
    imglist=sorted(list(set(os.listdir(dir))-set(done)))

g.close()