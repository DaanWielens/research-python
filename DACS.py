# -*- coding: utf-8 -*-
# QT IVVI DAC controller
# Version 1.0 (2020-02-05)
# Daan Wielens (ICE/QTM)

# PUT YOUR COM PORT HERE:
COMport = 1

import sys
from datetime import datetime

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
# Testing GUI on a pc without VISA / pySerial:
if len(sys.argv) == 2:
    if sys.argv[1] == '--novisa':
        novisa = 1
    else:
        print('Warning: your input argument (' + sys.argv[1] + ') is not recognized by this program and will be ignored. Please use --novisa if you want to simulate the GUI.')

# Initialise connection
if novisa == 0:   
    import serial
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM' + str(COMport)
    ser.parity = serial.PARITY_ODD
    ser.stopbits = 1
    ser.bytesize = 8
    ser.timeout = 1
    
def write_dac(dac, val):
    val = float(val)
    dac = int(dac)
    
    if val > 2:
        print('DAC setpoint > 2. The setpoint will be set to 2.')
        val = 2
    elif val < -2:
        print('DAC setpoint < 2. The setpoint will be set to 2.')
        val = -2
        
    bytevalue = int(((val+2)/4) * 65535).to_bytes(length=2, byteorder='big') 
    set_msg = bytes([7, 0, 2, 1, dac]) + bytevalue
    ser.open()
    ser.write(set_msg)
    ser.read(2)
    ser.close()        

def UpdateValues():
    if novisa == 0:
        # Read values, but also test connection and update the label
        try:
            ser.open()
            # Open port, request values of all DACs, close port, process data, output to text boxes
            read_msg = bytes([4, 0, 34, 2])
            ser.write(read_msg)
            resp = ser.read(34)
            ser.close()
            if len(resp) == 0:
                raise Exception
            now = datetime.now()
            dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
            lblStatus.config(fg="Green")
            statText.set('Last seen: ' + dt_string)
        except Exception:
            lblStatus.config(fg="Red")
            statText.set('No COM connection')
            return
            
        values_int = list(range(16))
        values_Volts = list(range(16))
        for i in range(16):
            values_int[i] = int.from_bytes(resp[2*(i+1):4+2*i], byteorder='big')
            values_Volts[i] = round(((values_int[i]) / 65535 * 4 - 2), 8)
            try:
                exec("d"+str(i+1)+"val.delete(0, Tkinter.END)")
                exec("d"+str(i+1)+"val.insert(0, "+str(values_Volts[i])+")")
            except Exception:
                print('Not able to update text')
    else:
        try:
            for i in range(16):
                # Hack to dynamically change variable names - useful!
                exec("d"+str(i+1)+"val.insert(0, 'No COM')")
        except Exception:
            print('Not able to update text')

def WriteDacsZero():
    for i in range(16):
        write_dac(i+1, 0)
    UpdateValues()
    
# Write functions for all 16 DACs in a short (but not very Pythonic) way
for i in range(16):
    exec("def WriteDac"+str(i+1)+"():\n val = float(d"+str(i+1)+"val.get()); write_dac("+str(i+1)+", val); UpdateValues()")

# Create GUI
top = Tkinter.Tk()
top.lift()
top.title('IVVI DAC controller - v1.0 (2020-02-05)')

# Title bar
titleFont = font.Font(family="Helvetica", size=16, weight="bold")
titleText = Tkinter.Label(top, text="IVVI DAC controller", fg="white", bg="#00adef", font=titleFont).grid(row=0, columnspan=1000, sticky=Tkinter.W+Tkinter.E)
vLine1 = Tkinter.Frame(top, bg="black", width=580, height=1).grid(row=1, columnspan=1000)

# Main area
lblFont = font.Font(family="Helvetica", size=12)
headFont = font.Font(family="Helvetica", size=14, weight="bold")

# DACs 1-8 frame
fDAC1 = Tkinter.Frame(top, width=400, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fDAC1.grid(row=2, padx=3, pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead1 = Tkinter.Label(fDAC1, text="DACs 1-8", font=headFont).grid(row=3, sticky=Tkinter.W+Tkinter.N)
vLine2 = Tkinter.Frame(fDAC1, bg="black", width=275, height=1).grid(row=4, columnspan=1000)

for i in range(8):
    exec("d"+str(i+1)+"lbl = Tkinter.Label(fDAC1, text='DAC " + str(i+1) + "', font=lblFont).grid(row=" + str(i+5) + ", sticky=Tkinter.W+Tkinter.N)")
    exec("d"+str(i+1)+"val = Tkinter.Entry(fDAC1, exportselection=0)")
    exec("d"+str(i+1)+"val.grid(row=" + str(i+5) + ", column=2, sticky=Tkinter.W)")
    exec("d"+str(i+1)+"unt = Tkinter.Label(fDAC1, text=' V   ', font=lblFont).grid(row=" + str(i+5) + ", column=3, sticky=Tkinter.W)")
    exec("d"+str(i+1)+"btn = Tkinter.Button(fDAC1, text='Set', command=WriteDac"+str(i+1)+").grid(row=" + str(i+5) + ", column=4, columnspan=1000, sticky=Tkinter.W)")

# DACs 9-16 frame
fDAC2 = Tkinter.Frame(top, width=500, height=400, relief=Tkinter.RIDGE, borderwidth=3)
fDAC2.grid(row=2, column=3, padx=(0, 3), pady=3, sticky=Tkinter.W+Tkinter.N)
lblHead2 = Tkinter.Label(fDAC2, text="DACs 9-16", font=headFont).grid(row=3, sticky=Tkinter.W+Tkinter.N)
vLine3 = Tkinter.Frame(fDAC2, bg="black", width=275, height=1).grid(row=4, columnspan=1000)

for i in range(8):
    exec("d"+str(i+9)+"lbl = Tkinter.Label(fDAC2, text='DAC " + str(i+9) + "', font=lblFont).grid(row=" + str(i+5) + ", sticky=Tkinter.W+Tkinter.N)")
    exec("d"+str(i+9)+"val = Tkinter.Entry(fDAC2, exportselection=0)")
    exec("d"+str(i+9)+"val.grid(row=" + str(i+5) + ", column=2, sticky=Tkinter.W)")
    exec("d"+str(i+9)+"unt = Tkinter.Label(fDAC2, text=' V   ', font=lblFont).grid(row=" + str(i+5) + ", column=3, sticky=Tkinter.W)")
    exec("d"+str(i+9)+"btn = Tkinter.Button(fDAC2, text='Set', command=WriteDac"+str(i+9)+").grid(row=" + str(i+5) + ", column=4, columnspan=1000, sticky=Tkinter.W)")

# Buttons
btnReadDACs = Tkinter.Button(top, text="Read DACs", command=UpdateValues).grid(row=10,column=0, sticky=Tkinter.W)
btnDACszero = Tkinter.Button(top, text="DACs to zero", command=WriteDacsZero).grid(row=10, column=0, padx=75, sticky=Tkinter.W)

# Status
statFont = font.Font(family="Helvetica", size=9)
statText = Tkinter.StringVar()
statText.set('Connection info here')
lblStatus = Tkinter.Label(top, textvariable=statText, font=statFont)
lblStatus.grid(row=10, column=3, sticky=Tkinter.W)
# Main loop(s)
UpdateValues()
top.mainloop()
