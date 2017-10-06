# -*- coding: utf-8 -*-
# Oxford IPS 120-10 Controller
# Version 1.3 (2017-10-06)
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

# Add dictionaries
global controlState
controlState = {
    '0': 'Local & Locked (default)',
    '1': 'Remote & Locked',
    '2': 'Local & Unlocked',
    '3': 'Remote & Unlocked'
}

global activityState
activityState = {
    '0': 'Hold',
    '1': 'To setpoint',
    '2': 'To zero',
    '3': 'Output clamped'
}

global modeState
modeState = {
    '0': 'At rest',
    '1': 'Sweeping',
    '2': 'Sweep limiting',
    '3': 'Sweeping and Sweep limiting',
}

def onClosingWindow():
    # Make absolutely sure that the session is closed properly.
    try:
        a = oxM.session
        oxM.write('R 7')
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        top.destroy()
    except Exception:
        top.destroy()

def clkGotoZero():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'
        oxM.write('A 2')
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        UpdateValues()

def clkGotoSetp():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'
        oxM.write('A 1')
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        UpdateValues()

def clkUnlock():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'
        oxM.write('C 3')
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        UpdateValues()

def clkHold():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'
        oxM.write('A 0')
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        UpdateValues()

def clkSetSetp():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'
        valSetp = setF.get().replace(',','.')
        numSetp = float(valSetp)
        if abs(numSetp) > 7:
            oxM.close()
            messagebox.showerror("Error","Setpoint exceeds limit of B = 7 T.")
            return
        oxM.write('J ' +  valSetp)
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        UpdateValues()

def clkSetRate():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'
        valRate = setR.get().replace(',','.')
        oxM.write('T ' +  valRate)
        oxM.wait_for_srq()
        oxM.read()
        oxM.close()
        UpdateValues()

def Refresher():
    UpdateValues()
    top.after(5000, Refresher)

def UpdateValues():
    if novisa == 0:
        oxM = rm.open_resource("GPIB0::25::INSTR")
        oxM.read_termination = '\r'

        oxM.write('R 7')
        oxM.wait_for_srq()
        FieldValue = oxM.read().strip('R+').replace('+','').replace('\n','').replace('\r','')

        oxM.write('R 8')
        oxM.wait_for_srq()
        FieldSetpValue = oxM.read().strip('R+').replace('+','').replace('\n','').replace('\r','')

        oxM.write('R 9')
        oxM.wait_for_srq()
        SweepRateValue = oxM.read().strip('R+').replace('+','').replace('\n','').replace('\r','')

        oxM.write('X')
        oxM.wait_for_srq()
        ExamineValue = oxM.read().strip('R+').replace('+','').replace('\n','').replace('\r','')
        controlStateValue = controlState[ExamineValue[6]]
        activityStateValue = activityState[ExamineValue[4]]
        modeStateValue = modeState[ExamineValue[11]]

        oxM.close()
        try:
            fvalue.set(FieldValue + ' T')
            fsetp.set(FieldSetpValue + ' T')
            sweepr.set(SweepRateValue +  ' T/min')
            contstat.set(controlStateValue)
            actstat.set(activityStateValue)
            modestat.set(modeStateValue)
        except Exception:
            print('Failed to update the GUI.')
    else:
        fvalue.set('noVISA')
        fsetp.set('noVISA')
        sweepr.set('noVISA')
        contstat.set('noVISA')
        actstat.set('noVISA')
        modestat.set('noVISA')

# Initialise VISA
if novisa == 0:
    import visa
    rm = visa.ResourceManager()

# Create GUI
top = Tkinter.Tk()
top.lift()
top.title('Oxford Magnet Controller')

# Title bar
titleFont = font.Font(family="Helvetica", size=16, weight="bold")
titleText = Tkinter.Label(top, text="Oxford IPS 120-10 Magnet Controller", fg="white", bg="#004af5", font=titleFont).grid(row=0, columnspan=1000, sticky=Tkinter.W+Tkinter.E)
vLine1 = Tkinter.Frame(top, bg="black", width=678, height=1).grid(row=1, columnspan=1000)

# Main area
lblFont = font.Font(family="Helvetica", size=12)
headFont = font.Font(family="Helvetica", size=14, weight="bold")

# Information frame
fInfo = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fInfo.grid(row=2, padx=3, pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead1 = Tkinter.Label(fInfo, text="Magnet status", font=headFont).grid(row=3, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblField1 = Tkinter.Label(fInfo, text="Magnetic field: ", font=lblFont).grid(row=4, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblSetp1 = Tkinter.Label(fInfo, text="Field setpoint: ", font=lblFont).grid(row=5, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblSweep1 = Tkinter.Label(fInfo, text="Sweep rate: ", font=lblFont).grid(row=6, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
vLine2 = Tkinter.Frame(fInfo, bg="black", width=275, height=1).grid(row=7, columnspan=1000)
lblCont1 = Tkinter.Label(fInfo, text="Control state: ", font=lblFont).grid(row=8,sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblAct1 = Tkinter.Label(fInfo, text="Activity state: ", font=lblFont).grid(row=9, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblMode1 = Tkinter.Label(fInfo, text="Mode state: ", font=lblFont).grid(row=10, sticky=Tkinter.W+Tkinter.N, pady=(5,0))

global fvalue
fvalue = Tkinter.StringVar()
fvalue.set("...,.. T")
lblField2 = Tkinter.Label(fInfo, textvariable=fvalue, font=lblFont).grid(row=4, column=1, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global fsetp
fsetp = Tkinter.StringVar()
fsetp.set("...,.. T")
lblSetp2 = Tkinter.Label(fInfo, textvariable=fsetp, font=lblFont).grid(row=5, column=1, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global sweepr
sweepr = Tkinter.StringVar()
sweepr.set("...,.. T/min")
lblSweep2 = Tkinter.Label(fInfo, textvariable=sweepr, font=lblFont).grid(row=6, column=1, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global contstat
contstat = Tkinter.StringVar()
contstat.set("......")
lblCont2 = Tkinter.Label(fInfo, textvariable=contstat, font=lblFont).grid(row=8, column=2, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global actstat
actstat = Tkinter.StringVar()
actstat.set("......")
lblAct2 = Tkinter.Label(fInfo, textvariable=actstat, font=lblFont).grid(row=9, column=2, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global modestat
modestat = Tkinter.StringVar()
modestat.set("......")
lblMode2 = Tkinter.Label(fInfo, textvariable=modestat, font=lblFont).grid(row=10, column=2, columnspan=1000, sticky = Tkinter.W, pady=(5,0))

# Controller frame
fSet = Tkinter.Frame(top, width=900, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fSet.grid(row=2, column=2, padx=(0, 3), pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead2 = Tkinter.Label(fSet, text="Magnet controls", font=headFont).grid(row=3, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblMan1 = Tkinter.Label(fSet, text= "Change setpoint to [T]: ", font=lblFont).grid(row=4, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
global setF
setF = Tkinter.Entry(fSet,exportselection=0)
setF.grid(row=4, column=3, columnspan=1000, sticky=Tkinter.W+Tkinter.N)
btnSetSetp = Tkinter.Button(fSet, text="Go!", command=clkSetSetp).grid(row=4,column=4, sticky = Tkinter.W+Tkinter.N, padx=(130,0))
lblMan1 = Tkinter.Label(fSet, text= "Change sweep rate to [T/min]: ", font=lblFont).grid(row=5, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
global setR
setR = Tkinter.Entry(fSet,exportselection=0)
setR.grid(row=5, column=3, columnspan=1000, sticky=Tkinter.W+Tkinter.N)
btnSetRate = Tkinter.Button(fSet, text="Go!", command=clkSetRate).grid(row=5,column=4, sticky = Tkinter.W+Tkinter.N, padx=(130,0))
lblFill = Tkinter.Label(fSet, text="     ", font=lblFont).grid(row=6, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
btnGotoZero = Tkinter.Button(fSet, text="Go to zero", command=clkGotoZero).grid(row=6,column=2, sticky = Tkinter.W+Tkinter.N)
btnGotoSetp = Tkinter.Button(fSet, text="Go to setpoint", command=clkGotoSetp).grid(row=6,column=2, sticky = Tkinter.W+Tkinter.N, padx=(71,0))
btnHold = Tkinter.Button(fSet, text="Hold", command=clkHold).grid(row=6,column=2, sticky = Tkinter.W+Tkinter.N, padx=(163,0))

vLine2 = Tkinter.Frame(fSet, bg="black", width=380, height=1).grid(row=7, columnspan=1000)

btnUnlock = Tkinter.Button(fSet, text="Unlock magnet", command=clkUnlock).grid(row=8, column=2, sticky=Tkinter.W+Tkinter.N)
lblFillx = Tkinter.Label(fSet, text="     ", font=lblFont).grid(row=9, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblFillx = Tkinter.Label(fSet, text="     ", font=lblFont).grid(row=10, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))

# Main loop(s)
UpdateValues()
Refresher()
top.protocol("WM_DELETE_WINDOW", onClosingWindow)
top.mainloop()
