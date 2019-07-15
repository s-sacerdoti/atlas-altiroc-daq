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

Configuration_LOAD_file = 'config/testBojan11.yml' # <= Path to the Configuration File to be Loaded

Number_of_pixels = 25
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


def runEventDisplay(pixel_data):
    toa_data = np.zeros(Number_of_pixels)
    tot_data = np.zeros(Number_of_pixels)
    hit_data = np.zeros(Number_of_pixels)

    #Generate pulse to test if this is working
    #for i in range(16):
    #    if (asicVersion == 1):
    #        top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
    #        time.sleep(0.001)
    #    else:
    #        top.Fpga[0].Asic.CalPulse.Start()
    #        time.sleep(0.001)

    print('hello')
    for pixel in pixel_data:
        toa_data[pixel.PixelIndex] = pixel.ToaData
        tot_data[pixel.PixelIndex] = pixel.TotData
        hit_data[pixel.PixelIndex] = pixel.Hit
        print(toa_data)
        print(tot_data)
        print(hit_data)
        print()
        #event_display.update(toa_data, tot_data, hits_toa_data, hits_tot_data):
    pixel_data.clear()
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


# Create the data reader streaming interface
deviceReader = top.dataStream[0]
# Create the fifo to ensure there is no back-pressure
fifo = rogue.interfaces.stream.Fifo(100, 0, True)
# Connect the device reader ---> fifo
pr.streamConnect(deviceReader, fifo) 

# Create the pixelreader streaming interface
dataStream = feb.MyPixelReader()
# Connect the fifo ---> stream reader
pr.streamConnect(fifo, dataStream) 
# Retrieve pixel data streaming object
pixel_data = dataStream.PixelData_list


#TODO: initialize pyplot display class here


while(True):
    try:
        time.sleep(0.5)
        runEventDisplay(pixel_data) #TODO: add display class as argument
    except KeyboardInterrupt:
        print('\n\nExiting Display and closing stream\n\n')
        break
        
top.stop()
