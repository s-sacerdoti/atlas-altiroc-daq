#!/usr/bin/env python3
##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

##############################################################################
# Script Settings

asicVersion = 1 # <= Select either V1 or V2 of the ASIC
DebugPrint = True
NofIterationsTOA = 16  # <= Number of Iterations for each Delay value
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)

#################################################################
                                                               ##
import sys                                                     ##
import rogue                                                   ##
import time                                                    ##
import random                                                  ##
import argparse                                                ##
                                                               ##
import pyrogue as pr                                           ##
import pyrogue.gui                                             ##
import numpy as np                                             ##
import common as feb                                           ##
                                                               ##
import os                                                      ##
import rogue.utilities.fileio                                  ##
                                                               ##
import statistics                                              ##
import math                                                    ##
import matplotlib.pyplot as plt                                ##
import setASICconfigs                                          ##
from setASICconfig_v2B6 import *                               ##
                                                               ##
#################################################################


def acquire_data(top, DelayRange, pixel_data): 
    pixel_stream = feb.PixelReader()    
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA

    for delay_value in DelayRange:
        top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(delay_value)

        for pulse_iteration in range(NofIterationsTOA):
            if (asicVersion == 1):
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.001)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)

        while pixel_stream.count < n_iterations: pass
        dataStream.count = 0
#################################################################


def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    
    #default parameters
    pixel_number = 4
    DAC_Vth = 320
    Qinj = 13 #10fc
    config_file = 'config/config_v2B6_noPAprobe.yml'
    dlyMin = 2250 
    dlyMax = 2700 
    dlyStep = 10
    
    
    # Add arguments
    parser.add_argument("--ip", type = str, required = True, help = "IP address")  
    parser.add_argument("--cfg", type = str, required = False, default = config_file, help = "config file")
    parser.add_argument("--ch", type = int, required = False, default = pixel_number, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = Qinj, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--delayMin", type = int, required = False, default = dlyMin, help = "scan start")
    parser.add_argument("--delayMax", type = int, required = False, default = dlyMax, help = "scan stop")
    parser.add_argument("--delayStep", type = int, required = False, default = dlyStep, help = "scan step")

    # Get the arguments
    args = parser.parse_args()
    return args
#################################################################


args = parse_arguments()
DelayRange = range( args.delayMin, args.delayMax, args.delayStep )

# Setup root class
top = feb.Top(ip= args.ip)    

# Load the default YAML file
print('Loading {Configuration_LOAD_file} Configuration File...')
top.LoadConfig(arg = args.cfg)

if DebugPrint:
    # Tap the streaming data interface (same interface that writes to file)
    dataStream = feb.MyEventReader()    
    pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

# Custom Configuration
set_fpga_for_custom_config(top,args.ch)

# Data Acquisition for TOA
pixel_data = []
acquire_data(top, DelayRange, pixel_data)

#######################
# Data Processing TOA #
#######################

HitCnt = []
DataMean = []
DataStdev = []

for delay_value in DelayRange:
    HitData = pixel_data[delay_value]
    HitCnt.append(len(HitData))
    if len(HitData) > 0:
        DataMean.append(np.mean(HitData, dtype=np.float64))
        DataStdev.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12))
    else:
        DataMean.append(0)
        DataStdev.append(0)

if len(DataMean) == 0:
    raise ValueError('No hits were detected during delay sweep. Aborting!')

# Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
index = np.where(np.sort(DataStdev))
MeanDataStdev = np.mean(np.sort(DataStdev)[index[0][0]:len(np.sort(DataStdev))])

# LSB estimation based on "DelayStep" value
index=np.where(DataMean)
fit = np.polyfit(Delay[index[0][5]:index[0][-5]], DataMean[index[0][5]:index[0][-5]], 1)
LSBest = DelayStep/abs(fit[0])


#################################################################
# Print Data
for delay_index, delay_value in enumerate(DelayRange):
    try:
        print('Delay = %d, HitCnt = %d, DataMean = %f LSB, DataStDev = %f LSB' % (delay_value, HitCnt[delay_index], DataMean[delay_index], DataStdev[delay_index]))
    except OSError:
        pass   
try:
    print('Maximum Measured TOA = %f LSB' % np.max(DataMean))
    print('Mean Std Dev = %f LSB' % MeanDataStdev)
except OSError:
    pass
for delay_index, delay_value in enumerate(Delay):
    try:
        print('Delay = %d, HitCnt = %d, DataMean = %f ps, DataStDev = %f ps' % (delay_value, HitCnt[delay_index], DataMean[delay_index]*LSBest, DataStdev[delay_index]*LSBest))
    except OSError:
        pass
try:
    print('Maximum Measured TOA = %f ps' % (np.max(DataMean)*LSBest))
    print('Mean Std Dev = %f ps' % (MeanDataStdev*LSBest))
    print('Average LSB estimate: %f ps' % LSBest)
except OSError:
    pass
#################################################################

#################################################################
# Plot Data
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))

# Plot (0,0) ; top left
ax1.plot(Delay, np.multiply(DataMean,LSBest))
ax1.grid(True)
ax1.set_title('TOA Measurment VS Programmable Delay Value', fontsize = 11)
ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
ax1.legend(['LSB estimate: %f ps' % LSBest],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
ax1.set_xlim(left = np.min(Delay), right = np.max(Delay))
ax1.set_ylim(bottom = 0, top = np.max(np.multiply(DataMean,LSBest))+100)

# Plot (0,1) ; top right
ax2.scatter(Delay, np.multiply(DataStdev,LSBest))
ax2.grid(True)
ax2.set_title('TOA Jitter VS Programmable Delay Value', fontsize = 11)
ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
ax2.set_ylabel('Std. Dev. [ps]', fontsize = 10)
ax2.legend(['Average Std. Dev. = %f ps' % (MeanDataStdev*LSBest)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
ax2.set_xlim(left = np.min(Delay), right = np.max(Delay))
ax2.set_ylim(bottom = 0, top = np.max(np.multiply(DataStdev,LSBest))+20)

# Plot (1,0) ; bottom left

delay_index_to_plot = -1
for delay_value in DelayRange: #find a good delay value to plot
    #I'd say having 80% of hits come back is good enough to plot
    if HitCnt[delay_value] > NofIterationsTOA * 0.8:
        delay_index_to_plot = delay_value
        break

if delay_index_to_plot != -1:
    hist_range = 10
    binlow = ( int(DataMean[delay_index_to_plot])-hist_range ) * LSBest
    binhigh = ( int(DataMean[delay_index_to_plot])+hist_range ) * LSBest
    hist_bin_list = np.arange(binlow, binhigh, LSBest)
    ax3.hist(np.multiply(pixel_data[delay_index_to_plot],LSBest), bins = hist_bin_list, align = 'left', edgecolor = 'k', color = 'royalblue')
    ax3.set_title('TOA Measurment for Programmable Delay = %d' % DelayRange[delay_index_to_plot], fontsize = 11)
    ax3.set_xlabel('TOA Measurement [ps]', fontsize = 10)
    ax3.set_ylabel('N of Measrements', fontsize = 10)
    ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMean[delay_index_to_plot]*LSBest, DataStdev[delay_index_to_plot]*LSBest, HitCnt[delay_index_to_plot])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)

# Plot (1,1)
ax4.plot(Delay, HitCnt)
ax4.grid(True)
ax4.set_title('TOA Valid Counts VS Programmable Delay Value', fontsize = 11)
ax4.set_xlabel('Programmable Delay Value', fontsize = 10)
ax4.set_ylabel('Valid Measurements', fontsize = 10)
ax4.set_xlim(left = np.min(Delay), right = np.max(Delay))
ax4.set_ylim(bottom = 0, top = np.max(HitCnt)*1.1)

plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
plt.show()
#################################################################

time.sleep(0.5)
# Close
top.stop()
