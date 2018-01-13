# Script to capture data from a Tektronix Oscilloscope via onboard USB-VISA.
# Data conversion based on: https://www.youtube.com/watch?v=6W4VrbtloYk
# Dependencies: pyVISA v1.6+, numpy, matplotlib

import visa
import numpy as np
from struct import unpack
import matplotlib.pyplot as plt
import sys
import getopt
import time
import os

# Usage
if len(sys.argv) == 1:
    print('Usage: python getwaveformTek.py <Options>')
    print('-----------------------------------------')
    print('Available options:\n')
    print('-p             plot data')
    print('-s filename    save data')
    print('-m             get "measure" data')
    sys.exit()

# Get program parameters
myopts, args = getopt.getopt(sys.argv[1:], "ps:m")
plotdata = False
savedata = False
domeasu = False
for o, a in myopts:
    if o == '-p':
        # Enable plotting
        plotdata = True
    elif o == '-s':
        # Save data
        savedata = True
        fname = a
    elif o == '-m':
        # Capture 'Measure' data
        domeasu = True

# Connect to device
rm = visa.ResourceManager()
tek = rm.open_resource('USB0::0x0699::0x0369::C052424::INSTR')

# Prepare scope for acquisition
tek.write('DATA:SOU CH1')
tek.write('DATA:WIDTH 1')
tek.write('DATA:ENC RPB')

# Get horz/vert settings from scope
ymult = float(tek.query('WFMPRE:YMULT?'))
yzero = float(tek.query('WFMPRE:YZERO?'))
yoff = float(tek.query('WFMPRE:YOFF?'))
xincr = float(tek.query('WFMPRE:XINCR?'))

# Acquire data and convert binary to data
tek.write('CURVE?')
data = tek.read_raw()
headerlen = 2 + int(data[1])
header = data[:headerlen]
ADCwave = data[headerlen:-1]
ADCwave = np.array(unpack('%sB' % len(ADCwave), ADCwave))

# Convert data to scale
V = (ADCwave - yoff) * ymult + yzero
t = np.arange(0, xincr * len(V), xincr)

# Get 'measure' data
if domeasu:
    # As we aqcuire data of CH1, make sure that we measure stats of CH1 as well
    for i in range(1, 6):
        tek.write('MEASU:MEAS' + str(i) + ':SOU CH1')

    # Let the scope change channels and acquire valid data before reading it
    time.sleep(1)

    # Get settings
    meas1set = tek.query('MEASU:MEAS1?').replace('"', '').split(';')
    meas2set = tek.query('MEASU:MEAS2?').replace('"', '').split(';')
    meas3set = tek.query('MEASU:MEAS3?').replace('"', '').split(';')
    meas4set = tek.query('MEASU:MEAS4?').replace('"', '').split(';')
    meas5set = tek.query('MEASU:MEAS5?').replace('"', '').split(';')

    # Get data
    meas1val = round(float(tek.query('MEASU:MEAS1:VAL?').replace('\n', '')), 3)
    meas2val = round(float(tek.query('MEASU:MEAS2:VAL?').replace('\n', '')), 3)
    meas3val = round(float(tek.query('MEASU:MEAS3:VAL?').replace('\n', '')), 3)
    meas4val = round(float(tek.query('MEASU:MEAS4:VAL?').replace('\n', '')), 3)
    meas5val = round(float(tek.query('MEASU:MEAS5:VAL?').replace('\n', '')), 3)

    # Convert settings to readable text
    measOptions = {
        'FREQUENCY': 'Frequency',
        'MEAN': 'Mean',
        'PERI': 'Period',
        'PK2PK': 'Peak-peak',
        'CRMS': 'Cyclic RMS',
        'RMS': 'RMS',
        'MINI': 'Minimum',
        'MAXI': 'Maximum',
        'RISE': 'Rise time',
        'FALL': 'Fall time',
        'PWIDTH': 'Positive pulse width',
        'NWIDTH': 'Negative pulse width',
        'NONE': 'None'
    }

    # Print data to console
    meas1str = measOptions[meas1set[0]] + ': ' + str(meas1val) + ' ' + meas1set[1]
    meas2str = measOptions[meas2set[0]] + ': ' + str(meas2val) + ' ' + meas2set[1]
    meas3str = measOptions[meas3set[0]] + ': ' + str(meas3val) + ' ' + meas3set[1]
    meas4str = measOptions[meas4set[0]] + ': ' + str(meas4val) + ' ' + meas4set[1]
    meas5str = measOptions[meas5set[0]] + ': ' + str(meas5val) + ' ' + meas5set[1]
    print(meas1str + '\n' + meas2str + '\n' + meas3str + '\n' + meas4str + '\n' + meas5str)

# Plot data
if plotdata:
    fig, ax = plt.subplots()
    ax.plot(t, V)
    ax.grid()
    ax.set_xlim(min(t), max(t))
    ax.set(xlabel='time (s)', ylabel='voltage (V)')

    if domeasu:
        titlelist = []
        measAstr = (meas1str, meas2str, meas3str, meas4str, meas5str)
        # Remove 'None' from list
        for i in measAstr:
            if 'None' not in i:
                titlelist.append(i)
        # Build title: max 2 values on top row, rest on bottom row
        titlestr = ''
        j = 0
        for i in titlelist:
            titlestr = titlestr + i + ', '
            j = j + 1
            if j == 2:
                titlestr = titlestr + '\n'
        titlestr = titlestr[:-2]
        ax.set(title=titlestr)

# Save data
if savedata:
    if not os.path.exists('Data'):
        os.makedirs('Data')

    with open('Data/' + fname + '.csv', 'w') as f:
        f.write('t (s), V (V)\n')
        for i in range(0, len(V)):
            f.write(str(t[i]) + ',' + str(V[i]) + '\n')

    if plotdata:
        fig.savefig('Data/' + fname + '.png')
        fig.savefig('Data/' + fname + '.pdf')

# Show plot in the end, as plt.show() stops executing other code
if plotdata:
    plt.show()
