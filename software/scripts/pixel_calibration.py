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

Configuration_LOAD_file = 'config/testBojan11.yml' # <= Path to the Configuration File to be Loaded

pixel_range_low = 3
pixel_range_high = 4
pixel_iteration = 1

DataAcqusitionTOA = 1   # <= Enable TOA Data Acquisition (Delay Sweep)

DelayRange_initial_low = 0     # <= low end of Programmable Delay Sweep search
DelayRange_initial_high = 4000     # <= high end of Programmable Delay Sweep search
DelayRange_initial_step_size = 100 # <= step size of initial delay range sweep
DelayRange_constriction_factor = 4 # <= how much tighter each new sweep is
DelayRange_final_size = 150 # <= length the optimal delay range should have

NofIterationsTOA = 16  # <= Number of Iterations for each Delay value


DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
Disable_CustomConfig = 0 # <= Disables the ASIC Configuration Customization inside the Script (Section Below) => all Configuration Parameters are taken from Configuration File   
##############################################################################

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
                                                               ##
#################################################################


def set_fpga_for_custom_config(top, pixel_number):
    for i in range(25):
        top.Fpga[0].Asic.SlowControl.disable_pa[i].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[i].set(0x1)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[i].set(0x0)

        top.Fpga[0].Asic.SlowControl.cBit_f_TOA[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_s_TOA[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_f_TOT[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_s_TOT[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_c_TOT[i].set(0x0)

    for i in range(16):
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)

    top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(0x30)

    top.Fpga[0].Asic.SlowControl.Write_opt.set(0x0)
    top.Fpga[0].Asic.SlowControl.Precharge_opt.set(0x0)

    top.Fpga[0].Asic.SlowControl.DLL_ALockR_en.set(0x1)
    top.Fpga[0].Asic.SlowControl.CP_b.set(0x5) #5
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlf_en.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.ext_Vcrtls_en.set(0x1) #1
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlc_en.set(0x0) #0

    top.Fpga[0].Asic.SlowControl.totf_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.totc_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.toa_satovfw.set(0x1)

    top.Fpga[0].Asic.SlowControl.SatFVa.set(0x3)
    top.Fpga[0].Asic.SlowControl.IntFVa.set(0x1)
    top.Fpga[0].Asic.SlowControl.SatFTz.set(0x4)
    top.Fpga[0].Asic.SlowControl.IntFTz.set(0x1)
    
    top.Fpga[0].Asic.SlowControl.cBitf.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cBits.set(0xf) #f
    top.Fpga[0].Asic.SlowControl.cBitc.set(0xf) #f

    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf)  #f
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf)  #f
    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(0x1) #0
    top.Fpga[0].Asic.SlowControl.cd[0].set(0x0) #6
    top.Fpga[0].Asic.SlowControl.dac_biaspa.set(0x10) #10
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(0x7) #7
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(0x19f) #173 / 183

    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(0x0)   # Rising edge of EXT_TRIG or CMD_PULSE delay
    top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0xfff) # Falling edge of EXT_TRIG (independent of CMD_PULSE)

    top.Fpga[0].Asic.Readout.StartPix.set(pixel_number)
    top.Fpga[0].Asic.Readout.LastPix.set(pixel_number)
#################################################################


def find_optimal_delay_range(top, dataStream, delay_range_low, delay_range_high, delay_range_step):
    delay_range_size = delay_range_high - delay_range_low
    if ( delay_range_size < DelayRange_final_size ):
        expansion_amount = DelayRange_final_size - delay_range_size
        delay_range_low -= int(expansion_amount / 2)
        delay_range_high += int(expansion_amount / 2)
        delay_range_step = 1


    print('\nSearching for delay range at step size ' + str(delay_range_step) + '\n')
    HitData_lengths = []
    weighted_sum = 0
    total_hits = 0
    optimal_HitData = []
    for delay_value in range( delay_range_low, delay_range_high, delay_range_step ):
        print('\nstep = %d' %delay_value)
        top.Fpga[0].Asic.Gpio.DlyCalPulseSet

        for i in range(NofIterationsTOA):
            if (asicVersion == 1):
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.001)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)

        time.sleep(0.1)

        HitData = dataStream.HitData
        weighted_sum += delay_value * len(HitData)
        total_hits += len(HitData)
        if delay_range_step == 1: optimal_HitData.append( HitData.copy() )
        print( str(total_hits) + ' ' + str(weighted_sum) )
        print(HitData)
        dataStream.HitData.clear()

    if delay_range_step == 1:
        return (delay_range_low, delay_range_high, recursion_level)
    else:
        #calculate weighted average of hit counts
        weighted_average = int(weighted_sum / total_hits)

        #create tighter delay range around weighted average
        tighter_step = delay_range_step / DelayRange_constriction_factor
        tighter_delay_radius = int( delay_range_size / (DelayRange_constriction_factor*2) )
        #If step size has dropped to 1, skip all other recursion steps by forcing delay_radius to zero
        if tighter_step < 1: tighter_delay_radius = 0
        tighter_delay_range_low = weighted_average - tighter_delay_radius
        tighter_delay_range_high = weighted_average + tighter_delay_radius
        print(weighted_average)
        print(tighter_delay_radius)
        print(tighter_delay_range_low)
        print(tighter_delay_range_high)
        return find_optimal_delay_range(top, dataStream, tighter_delay_range_low, tighter_delay_range_high, tighter_step)
    

    
#################################################################


def run_pixel_calibration(top, dataStream, pixel_number):
    # Custom Configuration
    if Disable_CustomConfig == 0: set_fpga_for_custom_config(top, pixel_number)

    find_optimal_delay_range(top, dataStream, DelayRange_initial_low, DelayRange_initial_high, DelayRange_initial_step_size)
#################################################################


# Set the argument parser
parser = argparse.ArgumentParser()

# Convert str to bool
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

# Add arguments
parser.add_argument(
    "--ip", 
    nargs    ='+',
    required = True,
    help     = "List of IP addresses",
)  
# Get the arguments
args = parser.parse_args()

# Setup root class
top = feb.Top(ip= args.ip)    

# Load the default YAML file
print('Loading Configuration File...')
top.LoadConfig(arg='config/defaults.yml')

# ... then load the User YAML file
top.LoadConfig(arg = Configuration_LOAD_file)

if DebugPrint:
    # Tap the streaming data interface (same interface that writes to file)
    debugStream = feb.MyEventReader()    
    pyrogue.streamConnect(top.dataStream[0], debugStream) # Assuming only 1 FPGA

# Create the data reader streaming interface
dataReader = top.dataStream[0]
# Create the Event reader streaming interface
dataStream = feb.MyFileReader()
# Connect the file reader ---> event reader
pr.streamConnect(dataReader, dataStream) 
print('stream connected!')


for pixel_number in range(pixel_range_low, pixel_range_high, pixel_iteration):
    run_pixel_calibration(top, dataStream, pixel_number) 



top.stop()
