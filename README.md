# High-Cadence-Imaging-III
Code supporting publication "High Cadence Optical Transient Searches using Drift Scan Imaging III: Development of an Inexpensive Drive Control System and Characterisation and Correction of Drive System Periodic Errors"

Abstract of the publication:
In order to further develop and implement novel drift scan imaging experiments to undertake wide field, high time resolution surveys for millisecond optical transients, an appropriate telescope drive system is required.  This paper describes the development of a simple and inexpensive hardware and software system to monitor, characterise, and correct the primary category of telescope drive errors, periodic errors due to imperfections in the drive and gear chain.  A model for the periodic errors is generated from direct measurements of the telescope drive shaft rotation, verified by comparison to astronomical measurements of the periodic errors.  The predictive model is generated and applied in real-time in the form of corrections to the drive rate.  A demonstration of the system shows that that inherent periodic errors of peak-to-peak amplitude ~100'' are reduced to below the seeing limit of ~3''.  This demonstration allowed an estimate of the uncertainties on the transient sensitivity timescales of the prototype survey of Tingay and Jjoubert (2021), with the nominal timescale sensitivity of 21 ms revised to be in the range of 20 - 22 ms, which does not significantly affect the results of the experiment.  The correction system will be adopted into the final version of high cadence imaging experiment, which is currently under construction.  The correction system is inexpensive (<$A100) and composed of readily available hardware, and is readily adaptable to other applications.  Design details and codes are therefore made publicly available.

The code included here runs in conjunction with the hardware implemented in the paper described above.  The codes included are:

https://github.com/steven-tingay/High-Cadence-Imaging-III/blob/main/telescope-tracker3.ino

https://github.com/steven-tingay/High-Cadence-Imaging-III/blob/main/pe-model-encoder-images.py


