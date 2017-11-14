# -*- coding: utf-8 -*-
# Oxford ITC503 Controller
# Version 1.0 (2017-10-20)
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
    '0': 'Heater manual, gas manual',
    '1': 'Heater auto, gas manual',
    '2': 'Heater manual, gas auto',
    '3': 'Heater auto, gas auto'
}

def onClosingWindow():
    # Make absolutely sure that the session is closed properly.
    try:
        a = ITC.session
        lib = rm.visalab
        lib.clear(a)
        ITC.close()
        top.destroy()
    except Exception:
        top.destroy()


def clkGotoZero():
    if novisa == 0:
        ITC = rm.open_resource("GPIB0::24::INSTR")
        ITC.read_termination = '\r'
        ITC.query('A 0')
        ITC.query('G 000')
        ITC.close()
        UpdateValues()

def clkGotoFull():
    if novisa == 0:
        ITC = rm.open_resource("GPIB0::24::INSTR")
        ITC.read_termination = '\r'
        ITC.query('A 0')
        ITC.query('G 999')
        ITC.close()
        UpdateValues()

def clkSetSetp():
    if novisa == 0:
        ITC = rm.open_resource("GPIB0::24::INSTR")
        ITC.read_termination = '\r'
        valSetp = setPerc.get().replace(',','').replace('.','')
        numSetp = abs(int(valSetp))
        if numSetp > 999:
            ITC.close()
            messagebox.showerror("Error","Setpoint exceeds limit of 99.9%.")
            return
        ITC.query('G ' +  valSetp)
        ITC.close()
        UpdateValues()

def Refresher():
    UpdateValues()
    top.after(5000, Refresher)

def UpdateValues():
    if novisa == 0:
        ITC = rm.open_resource("GPIB0::24::INSTR")
        ITC.read_termination = '\r'

        FlowSpaceTemp = ITC.query('R 1').strip('R+').replace('+','').replace('\n','').replace('\r','')
        GasFlowData = ITC.query('R 7').strip('R+').replace('+','').replace('\n','').replace('\r','')
        ExamineValue = ITC.query('X').strip('R+').replace('+','').replace('\n','').replace('\r','')
        controlStateValue = controlState[ExamineValue[5]]
        activityStateValue = activityState[ExamineValue[3]]

        ITC.close()
        try:
            flowvalue.set(FlowSpaceTemp + ' K')
            gasvalue.set(GasFlowData + ' %')
            contstat.set(controlStateValue)
            actstat.set(activityStateValue)
        except Exception:
            print('Failed to update the GUI.')
    else:
        flowvalue.set('noVISA')
        gasvalue.set('noVISA')
        contstat.set('noVISA')
        actstat.set('noVISA')

# Initialise VISA
if novisa == 0:
    import visa
    rm = visa.ResourceManager()

# Create GUI
top = Tkinter.Tk()
top.lift()
top.title('Oxford ITC503 Controller')

# Title bar
titleFont = font.Font(family="Helvetica", size=16, weight="bold")
titleText = Tkinter.Label(top, text="Oxford ITC503 Temperature Controller", fg="white", bg="#004af5", font=titleFont).grid(row=0, columnspan=1000, sticky=Tkinter.W+Tkinter.E)
vLine1 = Tkinter.Frame(top, bg="black", width=800, height=1).grid(row=1, columnspan=1000)

# Main area
lblFont = font.Font(family="Helvetica", size=12)
headFont = font.Font(family="Helvetica", size=14, weight="bold")

# Information frame
fInfo = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fInfo.grid(row=2, padx=3, pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead1 = Tkinter.Label(fInfo, text="Controller status", font=headFont).grid(row=3, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblFlow1 = Tkinter.Label(fInfo, text="Flow space temperature: ", font=lblFont).grid(row=4, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblGas1 = Tkinter.Label(fInfo, text="Gas flow: ", font=lblFont).grid(row=5, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
vLine2 = Tkinter.Frame(fInfo, bg="black", width=400, height=1).grid(row=6, columnspan=1000)
lblCont1 = Tkinter.Label(fInfo, text="Control state: ", font=lblFont).grid(row=7,sticky=Tkinter.W+Tkinter.N, pady=(5,0))

global flowvalue
flowvalue = Tkinter.StringVar()
flowvalue.set("...,.. K")
lblFLow2 = Tkinter.Label(fInfo, textvariable=flowvalue, font=lblFont).grid(row=4, column=1, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global gasvalue
gasvalue = Tkinter.StringVar()
gasvalue.set("...,.. %")
lblGas2 = Tkinter.Label(fInfo, textvariable=gasvalue, font=lblFont).grid(row=5, column=1, columnspan=1000, sticky = Tkinter.W, pady=(5,0))
global contstat
contstat = Tkinter.StringVar()
contstat.set("......")
lblCont2 = Tkinter.Label(fInfo, textvariable=contstat, font=lblFont).grid(row=7, column=2, columnspan=1000, sticky = Tkinter.W, pady=(5,0))

# Controller frame
fSet = Tkinter.Frame(top, width=900, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fSet.grid(row=2, column=2, padx=(0, 3), pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead2 = Tkinter.Label(fSet, text="Needle valve controls", font=headFont).grid(row=3, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
lblMan1 = Tkinter.Label(fSet, text= "Change setpoint to [%]: ", font=lblFont).grid(row=4, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
global setPerc
setPerc = Tkinter.Entry(fSet,exportselection=0)
setPerc.grid(row=4, column=3, columnspan=1000, sticky=Tkinter.W+Tkinter.N)
btnSetSetp = Tkinter.Button(fSet, text="Go!", command=clkSetSetp).grid(row=4,column=4, sticky = Tkinter.W+Tkinter.N, padx=(130,0))
lblFill = Tkinter.Label(fSet, text="     ", font=lblFont).grid(row=6, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
btnGotoZero = Tkinter.Button(fSet, text="Go to 00.0%", command=clkGotoZero).grid(row=6,column=2, sticky = Tkinter.W+Tkinter.N)
btnGotoFull = Tkinter.Button(fSet, text="Go to 99.9%", command=clkGotoFull).grid(row=6,column=2, sticky = Tkinter.W+Tkinter.N, padx=(81,0))

vLine2 = Tkinter.Frame(fSet, bg="black", width=380, height=1).grid(row=7, columnspan=1000)
lblAct1 = Tkinter.Label(fSet, text="Activity state: ", font=lblFont).grid(row=8, column=2, sticky=Tkinter.W+Tkinter.N, pady=(5,0))
global actstat
actstat = Tkinter.StringVar()
actstat.set("......")
lblAct2 = Tkinter.Label(fSet, textvariable=actstat, font=lblFont).grid(row=8, column=2, columnspan=1000, sticky = Tkinter.W, pady=(5,0), padx=(100,0))

# Buttons
#btnSetTemp = Tkinter.Button(top, text="Set temperature", command=clkSetTemp).grid(row=10,column=0, sticky = Tkinter.W)


# Main loop(s)
UpdateValues()
Refresher()
top.protocol("WM_DELETE_WINDOW", onClosingWindow)
top.mainloop()
