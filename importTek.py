# Script for importing data from a Tektronix Oscilloscope that has been saved
# to a USB flash drive.

import sys
import matplotlib.pyplot as plt


def readcsv(fname, savetofile=True):
    xdata = []
    ydata = []
    with open(fname, 'r') as file:
        rdata = file.readlines()[18:]
        i = 0
        for line in rdata:
            sline = line.split(',')
            xdata.append(float(sline[3]))
            ydata.append(float(sline[4]))

    if savetofile:
        wname = fname.split('.')[0]
        with open(wname + '_data.csv', 'w') as wfile:
            for i in range(0, len(xdata)):
                wfile.write(str(xdata[i]) + ',' + str(ydata[i]) + '\n')

    return (xdata, ydata)


def plotdata(savetofile=False, plttitle=None):
    data = readcsv(sys.argv[1], False)
    xdata = data[0]
    ydata = data[1]
    fig, ax = plt.subplots()
    ax.plot(xdata, ydata)
    ax.grid()
    ax.set_xlim(min(xdata), max(xdata))
    ax.set(xlabel='time (s)', ylabel='voltage (V)', title=plttitle)

    if savetofile:
        wname = fname.split('.')[0]
        fig.savefig(wname + '_plot.png')
        fig.savefig(wname + '_plot.pdf')

    plt.show()


# Standalone usage
global fname
if len(sys.argv) == 1:
    print('Please provide some arguments...')

if len(sys.argv) == 2:
    fname = sys.argv[1]
    readcsv(fname)

if len(sys.argv) == 3:
    fname = sys.argv[1]
    optn = sys.argv[2]
    if optn == '-r':
        readcsv(fname)
    if optn == '-p':
        plotdata()

if len(sys.argv) == 4:
    fname = sys.argv[1]
    optn = sys.argv[2]
    optval = sys.argv[3]

    if optn == '-r':
        if optval == 'True':
            readcsv(fname, True)
        if optval == 'False':
            readcsv(fname, False)
    if optn == '-p':
        if optval == 'True':
            plotdata(True)
        elif optval == 'False':
            plotdata(False)
        else:
            plotdata(True, optval)
