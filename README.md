# Research Tools in Python
This repository is devoted to small programs that might be useful during measurements with several instruments. I have written these programs in order be able to control more parameters of the instruments without having to rewrite parts of the LabVIEW interfaces that we use. 

### Requirements
In order to run the programs one must have python installed (either version 2.7.x or version 3). The python module PyVISA must be installed as well ( `pip install -U pyvisa` ). Also, NI-VISA must be installed on the computer. Follow the manual of PyVISA to install it: <https://pyvisa.readthedocs.io/en/stable/getting_nivisa.html#getting-nivisa>

## Graphical User Interfaces for experimental controllers
*IPS120*
---
Program to control the _Oxford IPS 120-10 Magnet Controller_
* Unlock magnet after startup
* Change magnet state (go to zero, go to setpoint, hold)
* Set values for setpoint and sweep rate
* Read magnet values periodically (every 5 sec)

*ITC503*
---
Program to control the _Oxford ITC503 Temperature Controller_
* Read values periodically (every 5 sec)
* Control gas flow manually

*QT IVVI DACs*
---
Program to control the _QuTech IVVI rack DAC module_
* Read values of all DACs
* Set values of a specific DAC
* Set all DACs to zero

Notes:
* The program requires the *pySerial* module to be installed. Furthermore, the user should change the number of the COM port in line 7 of the (current version of the) code. The script assumes 16 DACs to be installed in the IVVI rack.
* Since periodic readings could interfere with measurement scripts, the IVVI DACs controller does not have a 5 seconds refresh rate (such as the other scripts). If desirable, one can easily add this by using another GUI script as template.

Below is a screenshot of the GUI:

![alt IVVIScreenshot](https://github.com/DaanWielens/research-python/blob/master/docs/DacsControl.PNG?raw=true)

*Lake*
---
Program to control the _LakeShore 332 Temperature Controller_
* Read temperature values periodically (every 5 sec)
* Control temperature with PID loop

Below is a screenshot of the Lake GUI:

![alt LakeScreenshot](https://github.com/DaanWielens/research-python/blob/master/docs/LakeGUI.png?raw=true)

*SR830*
---
Program to control the _SR830 Lock-In Amplifier_
* Read settings
* Read data values manually

## Data acquisition and importing for Tektronix Oscilloscopes
*getwaveformTek*
---
Script that acquires waveform data from a Tektronix Oscilloscope (tested with _TektronixTDS2022B_).
Options:
```
- p             plot data
- m             also acquire data from 'measure' menu
- s filename    save data (and plot if combined with -p) to file(s)
```
This script requires numpy and matplotlib to be installed as well.

Example figure (obtained with `-p -m -s "500 Hz Sine"` as options):
![alt ExampleFigure](https://github.com/DaanWielens/research-python/blob/master/docs/500%20Hz%20Sine.png?raw=true)

*importTek*
---
Script that reads, converts and plots data, taken from a file that was saved by a Tektronix Oscilloscope to a USB flash drive. The script can be imported as module as well.
Options:
```
<None>          reads data and saves a copy of the data without header
-r              same as <None>
-r False        reads data, does not save data
-p <Boolean>    plots data; boolean determines if the plot should be saved or not
-p <Text>       plots and saves data, with <Text> being the title of the plot
```

This script requires matplotlib to be installed as well. 
