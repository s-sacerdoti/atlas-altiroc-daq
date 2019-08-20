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

DebugPrint = False

#Configuration_LOAD_file = 'config/config_v2B6_noPAprobe.yml' # <= Path to the Configuration File to be Loaded

Pixel_range_low = 4
Pixel_range_high = 5 #NOT inclusive
pixel_array = range(Pixel_range_low,Pixel_range_high)
Number_of_pixels = len(pixel_array)
No_hits_error_value = -1


DataAcqusitionTOA = 1   # <= Enable TOA Data Acquisition (Delay Sweep)

DelayRange_initial_low = 1000     # <= low end of Programmable Delay Sweep search
DelayRange_initial_high = 3000     # <= high end of Programmable Delay Sweep search
DelayRange_initial_step_size = 100 # <= step size of initial delay range sweep
DelayRange_final_step_size = 10 # <= step size that final optimal range will be stepped through with
DelayRange_constriction_factor = 8 # <= how much tighter each new sweep is
DelayRange_final_size = 150 # <= length the optimal delay range should have

NofIterationsTOA = 20  # <= Number of Iterations for each Delay value


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
from setASICconfig import set_pixel_specific_parameters        ##
                                                               ##
#################################################################


def scan_delay_range(top, delay_range, optimal_HitData):
    weighted_sum = 0
    total_hits = 0
    for delay_value in delay_range:
        top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(delay_value)

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
        if delay_range.step == DelayRange_final_step_size:
            optimal_HitData.append( HitData.copy() )

        print( '| {:>4} | {:>4} | {:>10} | {:>12} |'.format(
            delay_value, len(HitData), total_hits, weighted_sum)
        )
        #print(HitData)
        dataStream.HitData.clear()

    #calculate weighted average of hit counts
    if total_hits == 0: return No_hits_error_value
    weighted_hit_average = int(weighted_sum / total_hits)

    return weighted_hit_average
#################################################################


def find_optimal_delay_range(top, dataStream, delay_range, optimal_HitData):
    #Ensure delay range size is no smaller than specified minimum "DelayRange_final_size".
    #If it is, force step size to final value, and perform final sweep
    delay_range_size = delay_range.stop - delay_range.start
    if ( delay_range_size < DelayRange_final_size ):
        expansion = int( (DelayRange_final_size-delay_range_size) / 2 )
        delay_range = range( delay_range.start-expansion, delay_range.stop+expansion, DelayRange_final_step_size )

    #ensure delay range does not exceed initial boundaries
    if delay_range.start < DelayRange_initial_low:
        shift = DelayRange_initial_low - delay_range.start
        delay_range = range(DelayRange_initial_low, delay_range.stop+shift, delay_range.step)
    if delay_range.stop > DelayRange_initial_high:
        shift = delay_range.stop - DelayRange_initial_high 
        delay_range = range(delay_range.start-shift, DelayRange_initial_high, delay_range.step)

    print( '\nDelay Range = ' + str(delay_range) )
    print( '| step | hits | total_hits | weighted_sum |')
    weighted_hit_average = scan_delay_range(top, delay_range, optimal_HitData)
    if weighted_hit_average == No_hits_error_value: return No_hits_error_value

    #Recursively sweep over smaller delay ranges with smaller step sizes,
    #until we reach the final step size. Then simply return the optimal delay range.
    #The center of the next delay range is computed as the weighted average of the
    #pixels' hit counts. The next delay range is then expanded about this center
    #by an amount 'tighter_delay_radius'.
    if delay_range.step == DelayRange_final_step_size:
        return delay_range
    else:
        #create tighter delay range around weighted hit average
        tighter_step = int( delay_range.step / DelayRange_constriction_factor )
        tighter_delay_radius = int( delay_range_size / (DelayRange_constriction_factor*2) )

        #If step size has dropped to final size,
        #skip all other recursion steps by forcing delay_radius to zero.
        #Then at the beginning of the next call to find_optimal_delay_range,
        #the zero size delay range will be expanded to the required minumum final size.
        if tighter_step < DelayRange_final_step_size:
            tighter_delay_radius = 0

        tighter_delay_range_low = weighted_hit_average - tighter_delay_radius
        tighter_delay_range_high = weighted_hit_average + tighter_delay_radius
        tighter_delay_range = range( tighter_delay_range_low, tighter_delay_range_high, tighter_step)
        return find_optimal_delay_range(top, dataStream, tighter_delay_range, optimal_HitData)
#################################################################


def run_pixel_calibration(top, dataStream, pixel_number):
    print( '\n\n########################' )
    print( '# Calibrating pixel {:>2} #'.format(pixel_number) )
    print( '########################' )
    set_pixel_specific_parameters(top, pixel_number)

    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()

    #Determine optimal delay range for pixel
    initial_delay_range = range(DelayRange_initial_low, DelayRange_initial_high, DelayRange_initial_step_size)
    optimal_HitData = []
    optimal_delay_range = find_optimal_delay_range(top, dataStream, initial_delay_range, optimal_HitData)
    if optimal_delay_range == No_hits_error_value: 
        return (No_hits_error_value, 'No hits detected...')

    #Collect statistics about TOA data values
    DataMean = np.zeros( len(optimal_HitData) )
    DataStdev = np.zeros( len(optimal_HitData) )
    for delay_value, HitData_list in enumerate(optimal_HitData):
        if len(HitData_list) > 0:
            DataMean[delay_value] = np.mean(HitData_list, dtype=np.float64)
            DataStdev[delay_value] = math.sqrt(math.pow(np.std(HitData_list, dtype=np.float64),2)+1/12)
  
    # The following calculations ignore points with no data (i.e. Std.Dev = 0)
    nonzero = DataMean != 0

    # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
    MeanDataStdev = np.mean( DataStdev[nonzero] )

    # LSB estimation based on "DelayStep" value, again ignoring zero values
    safety_bound = 5
    Delay = np.array(optimal_delay_range)
    fit_x_values = Delay[nonzero][safety_bound:-safety_bound]
    fit_y_values = DataMean[nonzero][safety_bound:-safety_bound]
    linear_fit_slope = np.polyfit(fit_x_values, fit_y_values, 1)[0]
    LSB_est = DelayStep/abs(linear_fit_slope)

    return (LSB_est, optimal_delay_range)
#################################################################


# Set the argument parser
parser = argparse.ArgumentParser()

# Convert str to bool
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

config_file = 'config/measureTOA_B7.yml' # <= Path to the Configuration File to be Loaded
ipIN=['192.168.1.10']

# Add arguments
parser.add_argument( "--ip", nargs    ='+', required = True, help     = "List of IP addresses",)  
parser.add_argument( "--cfg", required = False, default = config_file, help = "Select yml configuration file to load")  
# Get the arguments
args = parser.parse_args()

# Setup root class
Configuration_LOAD_file = args.cfg
top = feb.Top(ip = args.ip, userYaml = [Configuration_LOAD_file])

if DebugPrint:
    top.Fpga[0].AxiVersion.printStatus()
    # Tap the streaming data interface (same interface that writes to file)
    debugStream = feb.PrintEventReader()    
    pyrogue.streamTap(top.dataStream[0], debugStream) # Assuming only 1 FPGA

# Create the data reader streaming interface
dataReader = top.dataStream[0]
# Create the Event reader streaming interface
dataStream = feb.PixelReader()
# Connect the file reader ---> event reader
pr.streamConnect(dataReader, dataStream) 


LSB_estimate_array = np.zeros(Number_of_pixels)
range_list = [0]*Number_of_pixels
for i_pix in range(Number_of_pixels):
    LSB_est, optimal_range = run_pixel_calibration(top, dataStream, pixel_array[i_pix])
    LSB_estimate_array[i_pix] = LSB_est
    range_list[i_pix] = optimal_range

#print results
print('\n\n\n')
print('#################')
print('# Final Results #')
print('#################')
print('Pixel | LSB_est | Range')
print('------+---------+------------')
for i_pix in range(Number_of_pixels):
    pixel_number=pixel_array[i_pix]
    print( '   {:<2} | {:<7.3f} | {}'.format(pixel_number, LSB_estimate_array[i_pix], range_list[i_pix]) )

top.stop()
