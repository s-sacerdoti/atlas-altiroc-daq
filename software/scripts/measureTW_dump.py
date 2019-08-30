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
# Script Settings

asicVersion = 1 # <= Select either V1 or V2 of the ASIC
DebugPrint = True
NofIterationsTOA = 16  # <= Number of Iterations for each Delay value
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
DelayValueTOT = 100       # <= Value of Programmable Delay for TOT Pulser Sweep
fallEdge = 3000

##############################################################################
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
#################################################################
# Set the argument parser
def parse_arguments():
    parser = argparse.ArgumentParser()

    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

    #default parameters
    pixel = 4
    DAC_Vth = 310
    Qinj = 13 #10fc
    config_file = 'config/config_v2B6_noPAprobe.yml'
    minPulser = 0
    maxPulser = 20
    PulserStep = 2
    DelayValue = 2400


    # Add arguments
    parser.add_argument("--ip", nargs ='+', required = True, help = "List of IP address")
    parser.add_argument("--cfg", type = str, required = False, default = config_file, help = "config file")
    parser.add_argument("--ch", type = int, required = False, default = pixel, help = "channel")
    parser.add_argument("--Vth", type = int, required = False, default = DAC_Vth, help = "threshold DAC")
    parser.add_argument("--delay", type = int, required = False, default = DelayValue, help = "delay")
    parser.add_argument("--minQ", type = int, required = False, default = minPulser, help = "scan start")
    parser.add_argument("--maxQ", type = int, required = False, default = maxPulser, help = "scan stop")
    parser.add_argument("--Qstep", type = int, required = False, default = PulserStep, help = "scan step")
    parser.add_argument("--out", type = str, required = False, default = 'testThreshold.txt', help = "output file name")  

    # Get the arguments
    args = parser.parse_args()
    return args

##############################################################################
##############################################################################
def acquire_data(range_low, range_high, range_step, top, 
        asic_pulser, file_prefix, n_iterations, dataStream): 
    
    asicVersion = 2 # <= Select either V1 or V2 of the ASIC

    for i in range(range_low, range_high, range_step):
        asic_pulser.set(i)
        ts = str(int(time.time()))
        val = '%d_' %i
        output_files = ['TestData/'+file_prefix+val+ts+'.txt']

        dataStream = feb.FrameToTextConverter(output_files)
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

        for j in range(n_iterations):
            if (asicVersion == 1): 
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.01)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)

        while dataStream.count < n_iterations: pass

        myfile = open(output_files[0],'a')
        myfile.write(dataStream.output_text_data[0])
        myfile.close()

#################################################################
#################################################################
def timewalk(argip, Configuration_LOAD_file, pixel_number, Vth,
      DelayValue, minPulser, maxPulser, PulserStep, outFile):

    LSBest = 20
    LSB_TOTc = 160
    LSB_TOTf = 40
    NofIterations = 20  # <= Number of Iterations for each Vth
    useProbe = False        #output discri probe
    pulser_list = range(minPulser,maxPulser,PulserStep)
    DebugPrint = True
    # Setup root class
    top = feb.Top(ip=argip)    
    
    # Load the default YAML file
    print(f'Loading {Configuration_LOAD_file} Configuration File...')
    top.LoadConfig(arg = Configuration_LOAD_file)
    
    if DebugPrint:
        # Tap the streaming data interface (same interface that writes to file)
        dataStream = feb.PrintEventReader()    
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA
    
    # Custom Configuration
    set_pixel_specific_parameters(top, pixel_number)
    #some more config
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(DelayValue)
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(Vth)

    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()
    
    #Take data
    acquire_data(minPulser, maxPulser, PulserStep, top, top.Fpga[0].Asic.SlowControl.dac_pulser, 'TW', NofIterations, dataStream)
    
    time.sleep(0.5)
    # Close
    top.stop()

#################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)
    timewalk(args.ip, args.cfg, args.ch, args.Vth,args.delay, args.minQ, args.maxQ, args.Qstep, args.out)
