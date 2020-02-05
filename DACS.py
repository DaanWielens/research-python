# -*- coding: utf-8 -*-
# QT IVVI DAC controller
# Version 1.0 (2020-02-05)
# Daan Wielens (ICE/QTM)

# PUT YOUR COM PORT HERE:
COMport = 1

import sys

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
        # Open port, request values of all DACs, close port, process data, output to text boxes
        ser.open()
        read_msg = bytes([4, 0, 34, 2])
        ser.write(read_msg)
        resp = ser.read(34)
        ser.close()
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
    
def WriteDac1():
    val = float(d1val.get())
    write_dac(1, val)
    UpdateValues()
    
def WriteDac2():
    val = float(d2val.get())
    write_dac(2, val)
    UpdateValues()
    
def WriteDac3():
    val = float(d3val.get())
    write_dac(3, val)
    UpdateValues()
    
def WriteDac4():
    val = float(d4val.get())
    write_dac(4, val)
    UpdateValues()

def WriteDac5():
    val = float(d5val.get())
    write_dac(5, val)
    UpdateValues()
    
def WriteDac6():
    val = float(d6val.get())
    write_dac(6, val)
    UpdateValues()
    
def WriteDac7():
    val = float(d7val.get())
    write_dac(7, val)
    UpdateValues()
    
def WriteDac8():
    val = float(d8val.get())
    write_dac(8, val)
    UpdateValues()

def WriteDac9():
    val = float(d9val.get())
    write_dac(9, val)
    UpdateValues()
    
def WriteDac10():
    val = float(d10val.get())
    write_dac(10, val)
    UpdateValues()
    
def WriteDac11():
    val = float(d11val.get())
    write_dac(11, val)
    UpdateValues()
    
def WriteDac12():
    val = float(d12val.get())
    write_dac(12, val)
    UpdateValues()

def WriteDac13():
    val = float(d13val.get())
    write_dac(13, val)
    UpdateValues()
    
def WriteDac14():
    val = float(d14val.get())
    write_dac(14, val)
    UpdateValues()
    
def WriteDac15():
    val = float(d15val.get())
    write_dac(15, val)
    UpdateValues()
    
def WriteDac16():
    val = float(d16val.get())
    write_dac(16, val)
    UpdateValues()

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
btnDACszero = Tkinter.Button(top, text="DACs to zero", command=WriteDacsZero).grid(row=10, column=0, padx=75, columnspan=2000, sticky=Tkinter.W)

# Main loop(s)
UpdateValues()
top.mainloop()
