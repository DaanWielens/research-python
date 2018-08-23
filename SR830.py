# -*- coding: utf-8 -*-
# Stanford Research Systems SR830 controller
# Version 1.0 (2017-05-08)
# Daan Wielens (ICE/QTM)

import sys
import time
import requests

try:
    # These modules will import succesfully for Python 2.x
    import Tkinter
    import ttk
    import tkMessageBox as messagebox
    import tkFont as font
except ImportError:
    # For Python 3.x, we need these (renamed) modules
    import tkinter as Tkinter
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import font

novisa = 0
# Testing GUI on a pc without VISA:
if len(sys.argv) == 2:
    if sys.argv[1] == '--novisa':
        novisa = 1
    else:
        print('Warning: your input argument (' + sys.argv[1] + ') is not recognized by this program and will be ignored. Please use --novisa if you want to simulate the GUI.')

# Initialise VISA
if novisa == 0:
    import visa
    rm = visa.ResourceManager()

# Dictionaries
global sensitivities
sensitivities = {
    '0': '2 nV',
    '1': '5 nV',
    '2': '10 nV',
    '3': '20 nV',
    '4': '50 nV',
    '5': '100 nV',
    '6': '200 nV',
    '7': '500 nV',
    '8': '1 uV',
    '9': '2 uV',
    '10': '5 uV',
    '11': '10 uV',
    '12': '20 uV',
    '13': '50 uV',
    '14': '100 uV',
    '15': '200 uV',
    '16': '500 uV',
    '17': '1 mV',
    '18': '2 mV',
    '19': '5 mV',
    '20': '10 mV',
    '21': '20 mV',
    '22': '50 mV',
    '23': '100 mV',
    '24': '200 mV',
    '25': '500 mV',
    '26': '1 V',
}

timeconstants = {
    '0': '10 us',
    '1': '30 us',
    '2': '100 us',
    '3': '300 us',
    '4': '1 ms',
    '5': '3 ms',
    '6': '10 ms',
    '7': '30 ms',
    '8': '100 ms',
    '9': '300 ms',
    '10': '1 s',
    '11': '3 s',
    '12': '10 s',
    '13': '30 s',
    '14': '100 s',
    '15': '300 s',
    '16': '1 ks',
    '17': '3 ks',
    '18': '10 ks',
    '19': '30 ks',
}

inputsources = {
    '0': 'A',
    '1': 'A-B',
    '2': 'I (1 MΩ)',
    '3': 'I (100 MΩ)',
}

inputground = {
    '0': 'Float',
    '1': 'Ground',
}

inputcoupling = {
    '0': 'AC',
    '1': 'DC',
}

reserves = {
    '0': 'High reserve',
    '1': 'Normal',
    '2': 'Low noise',
}

references = {
    '0': 'External',
    '1': 'Internal',
}

def convertUnits(inputval):
    # Check if number is written as scientific value
    numberlist = inputval.split('e')
    if len(numberlist) == 1:
        return inputval

    prefix = float(numberlist[0])
    suffix = int(numberlist[1])

    if suffix < -6:
        multiplier = 9-abs(suffix)
        prefix = prefix * 10**multiplier
        value = str("%.3f" % prefix) + ' n'
        return value

    if suffix < -3 and suffix >= -6:
        multiplier = 6-abs(suffix)
        prefix = prefix * 10**multiplier
        value = str("%.3f" % prefix) + ' u'
        return value

    if suffix < 0 and suffix >= -3:
        multiplier = 3-abs(suffix)
        prefix = prefix * 10**multiplier
        value = str("%.3f" % prefix) + ' m'
        return value

def SetGPIB():
    global GPIBaddress
    GPIBaddress = setGPIBtxt.get().replace('\n','').replace('\r','')
    try:
        GPIBaddress = int(GPIBaddress)
    except Exception:
        messagebox.showerror("Error","The GPIB address must be an integer value.")
        setGPIBtxt.delete(0, Tkinter.END)
        return

    if novisa == 0:
        SR = rm.open_resource("GPIB0::" + str(GPIBaddress) + "::INSTR")

        # Check if GPIB address points to a SR830 system
        try:
            identifier = SR.query("*IDN?")
        except Exception:
            messagebox.showerror('Error','There is no device responding to this GPIB address.')
            setGPIBtxt.delete(0, Tkinter.END)
            return
        if identifier.split(',')[1] != 'SR830':
            messagebox.showerror("Error","The selected GPIB address does not point to a SR830 system.")
            setGPIBtxt.delete(0, Tkinter.END)
            return

    ReadSettings()
    ReadValues()

def ReadSettings():
    global tConst
    global Sensi
    global sigInSrc
    global sigInGnd
    global sigInCpl
    global Resrv
    global Refsrc

    # Check if GPIB address is set
    if 'GPIBaddress' not in globals():
        messagebox.showerror("Error","Please set a GPIB address before trying to read settings.")
        return

    if novisa == 0:
        SR = rm.open_resource("GPIB0::" + str(GPIBaddress) + "::INSTR")
        getTimeconst = SR.query('OFLT?').replace('\n','').replace('\r','')
        txtTimec = str(getTimeconst)
        tConst.set(timeconstants[txtTimec])
        getSensitiv = SR.query('SENS?').replace('\n','').replace('\r','')
        txtSensitiv = str(getSensitiv)
        Sensi.set(sensitivities[txtSensitiv])
        getInpSrc = SR.query('ISRC?').replace('\n','').replace('\r','')
        txtInpSrc = str(getInpSrc)
        sigInSrc.set('Input: ' + inputsources[txtInpSrc])
        getInpGnd = SR.query('IGND?').replace('\n','').replace('\r','')
        txtInpGnd = str(getInpGnd)
        sigInGnd.set('Grounding: ' + inputground[txtInpGnd])
        getInpCpl = SR.query('ICPL?').replace('\n','').replace('\r','')
        txtInpCpl = str(getInpCpl)
        sigInCpl.set('Coupling: ' + inputcoupling[txtInpCpl])
        getResrv = SR.query('RMOD?').replace('\n','').replace('\r','')
        txtResrv = str(getResrv)
        Resrv.set(reserves[txtResrv])
        getRefsrc = SR.query('FMOD?').replace('\n','').replace('\r','')
        txtRefsrc = str(getRefsrc)
        Refsrc.set(references[txtRefsrc])
        SR.close()

    else:
        tConst.set('noVISA')
        Sensi.set('noVISA')
        sigInSrc.set('noVISA')
        sigInGnd.set('noVISA')
        sigInCpl.set('noVISA')
        Resrv.set('noVISA')
        Refsrc.set('noVISA')

def ReadValues():
    global readX
    global readY
    global readTheta
    global readFreq
    global readAmpl

    # Check if GPIB address is set
    if 'GPIBaddress' not in globals():
        messagebox.showerror("Error","Please set a GPIB address before trying to read values.")
        return

    if novisa == 0:
        SR = rm.open_resource("GPIB0::" + str(GPIBaddress) + "::INSTR")
        getData = SR.query('SNAP?1,2,4,9').replace('\n','').replace('\r','')
        txtData = str(getData)
        numberX = txtData.split(',')[0]
        numberY = txtData.split(',')[1]
        numberX = convertUnits(numberX)
        numberY = convertUnits(numberY)
        readX.set(numberX + 'V')
        readY.set(numberY + 'V')
        readTheta.set(txtData.split(',')[2] + ' deg')
        readFreq.set(txtData.split(',')[3] + ' Hz')
        getAmpl = SR.query('SLVL?').replace('\n','').replace('\r','')
        txtAmpl = str(getAmpl)
        readAmpl.set(txtAmpl + ' V')
        SR.close()

    else:
        readX.set('noVISA')
        readY.set('noVISA')
        readTheta.set('noVISA')
        readFreq.set('noVISA')
        readAmpl.set('noVISA')

# Create GUI
top = Tkinter.Tk()
top.lift()
top.title('SR830 Controller')

# Title bar
titleFont = font.Font(family="Helvetica", size=16, weight="bold")
titleText = Tkinter.Label(top, text="SR830 Controller", fg="white", bg="#a6211f", font=titleFont).grid(row=0, columnspan=1000, sticky=Tkinter.W+Tkinter.E)
vLine1 = Tkinter.Frame(top, bg="black", width=675, height=1).grid(row=1, columnspan=1000)

# Main area
lblFont = font.Font(family="Helvetica", size=12)
headFont = font.Font(family="Helvetica", size=14, weight="bold")

# Program settings frame
fSettings = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fSettings.grid(row=2, padx=3, pady=3, sticky=Tkinter.W+Tkinter.N, columnspan=1000)
lblSetHead = Tkinter.Label(fSettings, text="Program settings:", font=headFont).grid(row=3, sticky=Tkinter.W+Tkinter.N)
lblSetGPIB = Tkinter.Label(fSettings, text="GPIB address: [int]", font=lblFont).grid(row=4, sticky=Tkinter.W+Tkinter.N)
global setGPIBtxt
setGPIBtxt = Tkinter.Entry(fSettings,exportselection=0)
setGPIBtxt.grid(row=4, column=1, sticky=Tkinter.W+Tkinter.N)
btnSetGPIB = Tkinter.Button(fSettings, text="Set GPIB", command=SetGPIB).grid(row=4, column=2, columnspan=1000)

# Information frame
fInfo = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fInfo.grid(row=5, padx=3, pady=3, sticky=Tkinter.W+Tkinter.N)
lblHeader = Tkinter.Label(fInfo, text="Lock-In settings:", font=headFont).grid(row=6, sticky=Tkinter.W+Tkinter.N)
lblL1 = Tkinter.Label(fInfo, text="Time constant: ", font=lblFont).grid(row=7, sticky=Tkinter.W+Tkinter.N)
lblL2 = Tkinter.Label(fInfo, text="Sensitivity: ", font=lblFont).grid(row=8,sticky=Tkinter.W+Tkinter.N, pady=(3,0))
vLine2 = Tkinter.Frame(fInfo, bg="black", width=400, height=1).grid(row=9, columnspan=1000)
lblL3 = Tkinter.Label(fInfo, text="Signal input: ", font=lblFont).grid(row=10, sticky=Tkinter.W+Tkinter.N)
lblL4 = Tkinter.Label(fInfo, text="Reserve: ", font=lblFont).grid(row=13, sticky=Tkinter.W+Tkinter.N)
lblL5 = Tkinter.Label(fInfo, text="Reference source: ", font=lblFont).grid(row=14, sticky=Tkinter.W+Tkinter.N)

tConst = Tkinter.StringVar()
tConst.set("...,.. ms")
lblV1 = Tkinter.Label(fInfo, textvariable=tConst, font=lblFont).grid(row=7, column=1, columnspan=1000, sticky=Tkinter.W)
Sensi = Tkinter.StringVar()
Sensi.set("...,.. mV")
lblV2 = Tkinter.Label(fInfo, textvariable=Sensi, font=lblFont).grid(row=8, column=1, columnspan=1000, sticky=Tkinter.W)
sigInSrc = Tkinter.StringVar()
sigInSrc.set("....,....,....")
lblV3 = Tkinter.Label(fInfo, textvariable=sigInSrc, font=lblFont).grid(row=10, column=1, columnspan=1000, sticky=Tkinter.W)
sigInGnd = Tkinter.StringVar()
sigInGnd.set("....,....,....")
lblV3 = Tkinter.Label(fInfo, textvariable=sigInGnd, font=lblFont).grid(row=11, column=1, columnspan=1000, sticky=Tkinter.W)
sigInCpl = Tkinter.StringVar()
sigInCpl.set("....,....,....")
lblV3 = Tkinter.Label(fInfo, textvariable=sigInCpl, font=lblFont).grid(row=12, column=1, columnspan=1000, sticky=Tkinter.W)
Resrv = Tkinter.StringVar()
Resrv.set("........")
lblV4 = Tkinter.Label(fInfo, textvariable=Resrv, font=lblFont).grid(row=13, column=1, columnspan=1000, sticky=Tkinter.W)
Refsrc = Tkinter.StringVar()
Refsrc.set("........")
lblV5 = Tkinter.Label(fInfo, textvariable=Refsrc, font=lblFont).grid(row=14, column=1, columnspan=1000, sticky=Tkinter.W)

# Readings frame
fRead = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fRead.grid(row=5, column=2, padx=(0, 3), pady=3, sticky=Tkinter.W+Tkinter.N)
lblHeader = Tkinter.Label(fRead, text="Data values:", font=headFont).grid(row=6, sticky=Tkinter.W+Tkinter.N)
lblL1 = Tkinter.Label(fRead, text="X: ", font=lblFont).grid(row=7, sticky=Tkinter.W+Tkinter.N)
lblL2 = Tkinter.Label(fRead, text="Y: ", font=lblFont).grid(row=8,sticky=Tkinter.W+Tkinter.N, pady=(3,0))
vLine2 = Tkinter.Frame(fRead, bg="black", width=250, height=1).grid(row=9, columnspan=1000)
lblL3 = Tkinter.Label(fRead, text="Theta: ", font=lblFont).grid(row=10, sticky=Tkinter.W+Tkinter.N)
lblL4 = Tkinter.Label(fRead, text="Frequency: ", font=lblFont).grid(row=11, sticky=Tkinter.W+Tkinter.N)
lblL5 = Tkinter.Label(fRead, text="Sine amplitude: ", font=lblFont).grid(row=12, sticky=Tkinter.W+Tkinter.N)

readX = Tkinter.StringVar()
readX.set('....,.. V')
lvlV1 = Tkinter.Label(fRead, textvariable=readX, font=lblFont).grid(row=7, column=1, columnspan=1000, sticky=Tkinter.W)
readY = Tkinter.StringVar()
readY.set('....,.. V')
lvlV2 = Tkinter.Label(fRead, textvariable=readY, font=lblFont).grid(row=8, column=1, columnspan=1000, sticky=Tkinter.W)
readTheta = Tkinter.StringVar()
readTheta.set('....,.. deg')
lvlV3 = Tkinter.Label(fRead, textvariable=readTheta, font=lblFont).grid(row=10, column=1, columnspan=1000, sticky=Tkinter.W)
readFreq = Tkinter.StringVar()
readFreq.set('....,.. Hz')
lvlV4 = Tkinter.Label(fRead, textvariable=readFreq, font=lblFont).grid(row=11, column=1, columnspan=1000, sticky=Tkinter.W)
readAmpl = Tkinter.StringVar()
readAmpl.set('....,.. Hz')
lvlV5 = Tkinter.Label(fRead, textvariable=readAmpl, font=lblFont).grid(row=12, column=1, columnspan=1000, sticky=Tkinter.W)

# Buttons
fButton = Tkinter.Frame(top, width=400, height=400)
fButton.grid(row=15, pady=3, sticky=Tkinter.N+Tkinter.W)
btnReadSettings = Tkinter.Button(fButton, text="Read settings", command=ReadSettings).grid(row=16, column=0, sticky=Tkinter.W)
btnReadValues = Tkinter.Button(fButton, text="Read data values", command=ReadValues).grid(row=16, column=1, sticky=Tkinter.W)

# Main loop
top.mainloop()
