# -*- coding: utf-8 -*-
# LakeShore Temperature Controller
# Version 2.2 (2017-04-19)
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
global heatranges
heatranges = {'0': 'Off', '1': 'Low (0.5 W)', '2': 'Medium (5 W)', '3': 'High (50 W)'}

# Initialise VISA
if novisa == 0:
    import visa
    rm = visa.ResourceManager()

def UpdateValues():
    global temp
    global tempC
    global heatrange
    global heatranges
    global tempsetp
    if novisa == 0:
        Lake = rm.open_resource("GPIB0::12::INSTR")
        getTemp = Lake.query("KRDG?").replace('+','').replace('\n','').replace('\r','')
        getTempC = Lake.query("CRDG?").replace('+','').replace('\n','').replace('\r','')
        getHeatrange = Lake.query("RANGE?").replace('\n','').replace('\r','')
        getHeatout = Lake.query("HTR?").replace('+','').replace('\n','').replace('\r','')
        getTempsetp = Lake.query("SETP? 1").replace('+','').replace('\n','').replace('\r','')
        Lake.close()
        txtTemp = (str(getTemp) + " K").lstrip('0')
        txtTempC = (str(getTempC) + " °C").lstrip('0')
        txtHeatrange = str(getHeatrange)
        txtHeatout = (str(getHeatout) + " %")
        if txtHeatout == '000.0 %':
            txtHeatout = '0.0 %'
        else:
            txtHeatout = txtHeatout.lstrip('0')
        try:
            txtTempsetp = (str(getTempsetp) + " K").lstrip('0')
            temp.set(txtTemp)
            tempC.set(txtTempC)
            heatrange.set(heatranges[txtHeatrange])
            heatout.set(txtHeatout)
            tempsetp.set(txtTempsetp)
        except Exception:
            print('Failed to update the GUI.')
    else:
        temp.set('noVISA')
        tempC.set('noVISA')
        heatrange.set('noVISA')
        heatout.set('noVISA')
        tempsetp.set('noVISA')

def ReadPID():
    global Pcont
    global Icont
    global Dcont
    global manOut
    if novisa == 0:
        Lake = rm.open_resource("GPIB0::12::INSTR")
        getPID = str(Lake.query("PID? 1").replace('+','').replace('\n','').replace('\r',''))
        getManOut = str(Lake.query("MOUT? 1").replace('+','').replace('\n','').replace('\r',''))
        Lake.close()
        Pcont.set(getPID.split(',')[0].lstrip('0'))
        Icont.set(getPID.split(',')[1].lstrip('0'))
        Dcont.set(getPID.split(',')[2].lstrip('0'))
        manOut.set(getManOut)
    else:
        Pcont.set('noVISA')
        Icont.set('noVISA')
        Dcont.set('noVISA')
        manOut.set('noVISA')

def Refresher():
    UpdateValues()
    top.after(5000, Refresher)

def clkSetTemp():
    global sttop
    sttop = Tkinter.Toplevel(top)
    sttop.lift()
    sttop.title('Set temperature')

    # Title bar
    titleFont = font.Font(family="Helvetica", size=16, weight="bold")
    titleText = Tkinter.Label(sttop, text="Set temperature", fg="white", bg="#004aa5", font=titleFont).grid(row=0, columnspan=1000, sticky=Tkinter.W+Tkinter.E)
    vLine1 = Tkinter.Frame(sttop, bg="black", width=450, height=1).grid(row=1, columnspan=1000)

    # Main frame
    lblFont = font.Font(family="Helvetica", size=12)
    headFont = font.Font(family="Helvetica", size=14, weight="bold")
    lblHead = Tkinter.Label(sttop, text="Set temperature controller", font=headFont).grid(row=2, columnspan=1000, sticky=Tkinter.W+Tkinter.N)

    lblsetT = Tkinter.Label(sttop, text="Temperature setpoint (K)", font=lblFont).grid(row=3, sticky=Tkinter.W+Tkinter.N)
    lblrT = Tkinter.Label(sttop, text="[4.5 - 280]", font=lblFont).grid(row=3, column=1, sticky=Tkinter.E+Tkinter.N)
    global setT
    setT = Tkinter.Entry(sttop,exportselection=0)
    setT.grid(row=3, column=2, columnspan=1000, sticky=Tkinter.W)
    lblsetP = Tkinter.Label(sttop, text="P (proportional)", font=lblFont).grid(row=4, sticky=Tkinter.W+Tkinter.N)
    lblrP = Tkinter.Label(sttop, text="[0.1 - 1000]", font=lblFont).grid(row=4, column=1, sticky=Tkinter.E+Tkinter.N)
    global setP
    setP = Tkinter.Entry(sttop,exportselection=0)
    setP.grid(row=4, column=2, columnspan=1000, sticky=Tkinter.W)
    lblsetP = Tkinter.Label(sttop, text="I (integral)", font=lblFont).grid(row=5, sticky=Tkinter.W+Tkinter.N)
    lblrP = Tkinter.Label(sttop, text="[0.1 - 1000]", font=lblFont).grid(row=5, column=1, sticky=Tkinter.E+Tkinter.N)
    global setI
    setI = Tkinter.Entry(sttop,exportselection=0)
    setI.grid(row=5, column=2, columnspan=1000, sticky=Tkinter.W)
    lblsetD = Tkinter.Label(sttop, text="D (derivative)", font=lblFont).grid(row=6, sticky=Tkinter.W+Tkinter.N)
    lblrD = Tkinter.Label(sttop, text="[0 - 200]", font=lblFont).grid(row=6, column=1, sticky=Tkinter.E+Tkinter.N)
    global setD
    setD = Tkinter.Entry(sttop,exportselection=0)
    setD.grid(row=6, column=2, columnspan=1000, sticky=Tkinter.W)
    lblsetM = Tkinter.Label(sttop, text="Manual output", font=lblFont).grid(row=7, sticky=Tkinter.W+Tkinter.N)
    lblrM = Tkinter.Label(sttop, text="[0.0 - 100.0]", font=lblFont).grid(row=7, column=1, sticky=Tkinter.E+Tkinter.N)
    global setM
    setM = Tkinter.Entry(sttop,exportselection=0)
    setM.grid(row=7, column=2, columnspan=1000, sticky=Tkinter.W)
    lblsetH = Tkinter.Label(sttop, text="Heater range", font=lblFont).grid(row=8, sticky=Tkinter.W+Tkinter.N)
    global Hoptions
    Hoptions = ['Off', 'Low (0.5 W)', 'Medium (5 W)', 'High (50 W)']
    global setH
    setH = Tkinter.StringVar(sttop)
    setH.set(Hoptions[0])
    options = Tkinter.OptionMenu(sttop, setH, *Hoptions)
    options.config(width=16)
    options.grid(row=8, column=2, columnspan=1000, sticky=Tkinter.W)
    btnUpdateTemp = Tkinter.Button(sttop, text="Send values to controller", command=UpdatePID).grid(row=9)

def UpdatePID():
    valT = setT.get().replace(',','.')
    valP = setP.get().replace(',','.')
    valI = setI.get().replace(',','.')
    valD = setD.get().replace(',','.')
    valM = setM.get().replace(',','.')
    valH = str(Hoptions.index(setH.get()))
    if (len(valT) == 0 or len(valP) == 0 or len(valI) == 0 or len(valD) == 0 or len(valM) ==0):
        messagebox.showerror("Error","Please enter values in all fields!")
        sttop.lift()
        return

    print("Setting temperature setpoint: "+valT)
    print("Setting P (proportional):     "+valP)
    print("Setting I (integral):         "+valI)
    print("Setting D (derivative):       "+valD)
    print("Setting manual output:        "+valM)
    print("Setting heater range:         "+valH)

    if novisa == 0:
        try:
            Lake = rm.open_resource("GPIB0::12::INSTR")
            # Test the following lines of code tomorrow...
            Lake.query("SETP 1,"+valT)
            Lake.query("MOUT 1,"+valM)
            Lake.query("PID 1,"+valP+","+valI+","+valD)
            Lake.query("RANGE "+valH)
            Lake.close()
            print("Settings updated correctly!")
        except Exception:
            print("Unable to update settings on the Lake Shore controller.")

    time.sleep(1)
    ReadPID()
    sttop.destroy()

# Create GUI
top = Tkinter.Tk()
top.lift()
top.title('LakeShore Controller')

# Title bar
titleFont = font.Font(family="Helvetica", size=16, weight="bold")
titleText = Tkinter.Label(top, text="LakeShore Model 332 Temperature Controller", fg="white", bg="#004aa5", font=titleFont).grid(row=0, columnspan=1000, sticky=Tkinter.W+Tkinter.E)
vLine1 = Tkinter.Frame(top, bg="black", width=575, height=1).grid(row=1, columnspan=1000)

# Main area
lblFont = font.Font(family="Helvetica", size=12)
headFont = font.Font(family="Helvetica", size=14, weight="bold")

# Information frame
fInfo = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fInfo.grid(row=2, padx=3, pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead1 = Tkinter.Label(fInfo, text="Controller output", font=headFont).grid(row=3, sticky=Tkinter.W+Tkinter.N)
lblTemp1 = Tkinter.Label(fInfo, text="Temperature: ", font=lblFont).grid(row=4, sticky=Tkinter.W+Tkinter.N)
vLine2 = Tkinter.Frame(fInfo, bg="black", width=275, height=1).grid(row=6, columnspan=1000)
lblTset1 = Tkinter.Label(fInfo, text="Temperature setpoint: ", font=lblFont).grid(row=7,sticky=Tkinter.W+Tkinter.N, pady=(3,0))
lblHeat1 = Tkinter.Label(fInfo, text="Heater range: ", font=lblFont).grid(row=8, sticky=Tkinter.W+Tkinter.N)
lblHout1 = Tkinter.Label(fInfo, text="Heater output: ", font=lblFont).grid(row=9, sticky=Tkinter.W+Tkinter.N)

global temp
temp = Tkinter.StringVar()
temp.set("...,.. K")
lblTemp2 = Tkinter.Label(fInfo, textvariable=temp, font=lblFont).grid(row=4, column=1, columnspan=1000, sticky = Tkinter.W)
global tempC
tempC = Tkinter.StringVar()
tempC.set("...,.. °C")
lblTemp3 = Tkinter.Label(fInfo, textvariable=tempC, font=lblFont).grid(row=5, column=1, columnspan=1000, sticky = Tkinter.W)
global tempsetp
tempsetp = Tkinter.StringVar()
tempsetp.set("...,.. K")
lblTset2 = Tkinter.Label(fInfo, textvariable=tempsetp, font=lblFont).grid(row=7, column=2, columnspan=1000, sticky = Tkinter.W, pady=(3,0))
global heatrange
heatrange = Tkinter.StringVar()
heatrange.set("......")
lblHeat2 = Tkinter.Label(fInfo, textvariable=heatrange, font=lblFont).grid(row=8, column=2, columnspan=1000, sticky = Tkinter.W)
global heatout
heatout = Tkinter.StringVar()
heatout.set("...,.. %")
lblHout2 = Tkinter.Label(fInfo, textvariable=heatout, font=lblFont).grid(row=9, column=2, columnspan=1000, sticky = Tkinter.W)

# PID Controller frame
fPID = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fPID.grid(row=2, column=2, padx=(0, 3), pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead2 = Tkinter.Label(fPID, text="Loop 1 controls", font=headFont).grid(row=3, column=2, sticky=Tkinter.W+Tkinter.N)
lblMan1 = Tkinter.Label(fPID, text= "Manual output: ", font=lblFont).grid(row=4, column=2, sticky=Tkinter.W+Tkinter.N)
lblFill = Tkinter.Label(fPID, text="     ", font=lblFont).grid(row=5, column=2, sticky=Tkinter.W+Tkinter.N)
vLine2 = Tkinter.Frame(fPID, bg="black", width=275, height=1).grid(row=6, columnspan=1000)
lblP1 = Tkinter.Label(fPID, text="P (proportional): ", font=lblFont).grid(row=7, column=2, sticky=Tkinter.W+Tkinter.N, pady=(3,0))
lblI1 = Tkinter.Label(fPID, text="I (integral): ", font=lblFont).grid(row=8, column=2, sticky=Tkinter.W+Tkinter.N)
lblD1 = Tkinter.Label(fPID, text="D (derivative): ", font=lblFont).grid(row=9, column=2, sticky=Tkinter.W+Tkinter.N)
global manOut
manOut = Tkinter.StringVar()
manOut.set(".... %")
lblMan2 = Tkinter.Label(fPID, textvariable=manOut, font=lblFont).grid(row=4, column=3, sticky=Tkinter.W+Tkinter.N)
global Pcont
Pcont = Tkinter.StringVar()
Pcont.set("..")
lblP2 = Tkinter.Label(fPID, textvariable=Pcont, font=lblFont).grid(row=7, column=3, sticky=Tkinter.W+Tkinter.N, pady=(3,0))
global Icont
Icont = Tkinter.StringVar()
Icont.set("..")
lblP2 = Tkinter.Label(fPID, textvariable=Icont, font=lblFont).grid(row=8, column=3, sticky=Tkinter.W+Tkinter.N)
global Dcont
Dcont = Tkinter.StringVar()
Dcont.set("..")
lblP2 = Tkinter.Label(fPID, textvariable=Dcont, font=lblFont).grid(row=9, column=3, sticky=Tkinter.W+Tkinter.N)

# Buttons
btnSetTemp = Tkinter.Button(top, text="Set temperature", command=clkSetTemp).grid(row=10,column=0, sticky = Tkinter.W)

# Main loop(s)
UpdateValues()
ReadPID()
Refresher()
top.mainloop()
