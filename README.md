# Research Tools in Python
This repository is devoted to small programs that might be useful during measurements with several instruments. I have written these programs in order be able to control more parameters of the instruments without having to rewrite parts of the LabVIEW interfaces that we use. 

### Requirements
In order to run the programs one must have python installed (either version 2.7.x or version 3). The python module PyVISA must be installed as well ( `pip install -U pyvisa` ). Also, NI-VISA must be installed on the computer. Follow the manual of PyVISA to install it: <https://pyvisa.readthedocs.io/en/stable/getting_nivisa.html#getting-nivisa>

### Current list of programs and their functionalities
**IPS120**
---
Program to control the _Oxford IPS 120-10 Magnet Controller_
* Unlock magnet after startup
* Change magnet state (go to zero, go to setpoint, hold)
* Set values for setpoint and sweep rate
* Read magnet values periodically (every 5 sec)

**ITC503**
---
Program to control the _Oxford ITC503 Temperature Controller_
* Read values periodically (every 5 sec)
* Control gas flow manually

**Lake**
---
Program to control the _LakeShore 332 Temperature Controller_
* Read temperature values periodically (every 5 sec)
* Control temperature with PID loop

**SR830**
---
Program to control the _SR830 Lock-In Amplifier_
* Read settings
* Read data values manually
