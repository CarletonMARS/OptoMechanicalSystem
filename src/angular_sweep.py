# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 16:07:05 2025

@author: hrishitdas
"""

import os
# import rotary_stage
# import laser
import numpy as np
import pyvisa
import time
import csv

# # Define rotation stage parameters
start_angle = 26           # Minimum angle (degrees)
end_angle = 32              # Maximum angle (degrees)
rotation_step = 0.1       # Step size for rotation (degrees)
angleVect = np.arange(start_angle, end_angle, rotation_step)


# Define parameters
start_wavelength = 1520    # Starting wavelength (nm) : min- 1470nm!!! EDFA min- 1525
end_wavelength = 1570       # Ending wavelength (nm)   : max- 1580nm!!! EDFA max - 1565
P_out = -5                  #Sets Laser output power in dBm !!!Only set between -10dBm to 0dBm!!! EDFA Output is always constant- 17.7dBm
step_size = 1                 # Step size in nm
laser_stabilize_time = 2    # Time to wait for laser to stabilize (seconds)
osc_stablize_time = 1       # Time to wait for oscilloscope to stabilize (seconds)
term_res = 50               #termination resistance on oscilloscope in Ohms

output_folder = "./Data/"

#################################################################################################################################################
def set_rotary_angle(angle):
    """Moves stage to an absolute angle."""
    os.system(f"python console_interface.py move_to {angle}")
    time.sleep(2)  # Stabilization time

#os.system(f"python console_interface.py rotate -d {start_angle} r")  # Move from 0° to -3°

os.system("python console_interface.py rotate -d {} l".format(-start_angle))

# Initialize PyVISA resource manager
rm = pyvisa.ResourceManager()

# Connect to the HP8168-E Tunable Laser Source (tls) via GPIB
tls_address = 'GPIB1::20::INSTR'  # Replace with your GPIB address for the TLS
tls = rm.open_resource(tls_address)
tls.timeout = 3000  # Set to 3 seconds
tls.write(":OUTP ON") # Turns on Laser output
tls.write(f"SOUR:POW:LEV:IMM:AMP {P_out}") #Sets Laser output power in dBm (-5dBm = 0.3mW)
tls.write(":SOUR:MODOUT FRQRDY")  # Turns off modulation signal
laser_state = tls.query_ascii_values(":OUTP?") # 0.0 mean off and 1.0 means on 
print(f"Laser is now {laser_state}.")
#tls.timeout = 1000 #time delay in ms

# Connect to the R&S RTM2034 Oscilloscope via VISA
osc_address = 'USB0::0x0AAD::0x010F::101561::0::INSTR'  # Replace with your oscilloscope's IP address
osc = rm.open_resource(osc_address)
osc.timeout = 3000   # Set to 5 seconds
osc.write("FORM ASC")  # Set response format to ASCII
#osc.write("SING") #Command to set to single data acquisition
osc.write("CHAN2:COUP DC") #Command to set channel 2 for data measuremet via 50 ohm termination
#osc.timeout = 1000 #time delay in ms
val = osc.query("FORM?")
print(f"Oscilloscope is now {val}")




# Function to set wavelength on the TLS
def set_wavelength(wavelength):
    """
    Sets the wavelength of the tunable laser source.
    """
    tls.write(f"SOUR:WAVE:CW {wavelength}NM")
    time.sleep(2)  # Allow time for update
    
      
# Function to measure current using the oscilloscope
def measure_current():
    """
    Measures current from the power detector using the oscilloscope.
    Returns the measured value.
    """
    osc.write("SING") #Command to set to single data acquisition
    time.sleep(osc_stablize_time)       # wait for oscilloscope to send data
    voltage_values = np.mean(osc.query_ascii_values("CHAN2:DATA?"))
    #voltage_values = float(np.mean(osc.query("CHAN2:DATA?"))) # Command to measure current (adjust based on manual)
    current_values = voltage_values/term_res  # Read and convert to float
    #osc.timeout = osc_timeout
    return float(current_values)

# Perform wavelength sweep and collect data
def wavelength_sweep(start_wavelength, end_wavelength, step_size):
    pass


        
# Run the wavelength sweep
for angle in angleVect:
    
    """
    Sweeps through wavelengths and measures current at each step.
    Returns an array of wavelengths and corresponding measured currents.
    """
    # Using np.arange() instead of range() for float step sizes
    wavelengths = np.arange(start_wavelength, end_wavelength + step_size, step_size)
    data = [] #list to store results
    
    #For loop to sweep frequency and print in console
    
    for wavelength in wavelengths:
        print(f"Setting wavelength to {wavelength} nm...")
        set_wavelength(wavelength)  # Set TLS wavelength
        time.sleep(1)
        tls_wavelength = tls.query("SOUR:WAVE:CW?")
        print(f"Current wavelength is {tls_wavelength} m")
        
        print(f"Waiting for {laser_stabilize_time} seconds...")
        time.sleep(laser_stabilize_time)  # Wait for stabilization
        
        current = measure_current()  # Measure current from oscilloscope
        
        print("Measuring current...")
        data.append([wavelength, current])  # Append data
        
        time.sleep(2)
        print(f"Wavelength: {wavelength} nm, Current: {current} A")
        time.sleep(2)


# # Save data to CSV file
#     csv_filename = "wavelength_sweep_results.csv"
#     with open(csv_filename, mode="w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(["Wavelength (nm)", "Current (A)"])  # Header
#         writer.writerows(data)  # Write data

#     print(f"\n✅ Data saved to {csv_filename}")

# Save data to CSV file (named after the rotation angle)
    
    csv_filename = os.path.join(output_folder, f"{angle:.1f}.csv")
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Wavelength (nm)", "Current (A)"])  # Header
        writer.writerows(data)  # Write data
    
    # Increment the rotary stage
    os.system("python console_interface.py rotate -d {} r".format(rotation_step))
    time.sleep(2)
    
# Rotate back into position
#os.system("python console_interface.py rotate -d {} l".format(end_angle-start_angle))

tls.write(":OUTP OFF") # Turns off Laser output