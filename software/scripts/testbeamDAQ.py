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

DebugPrint = True
NofIterationsTOA = 16  # <= Number of Iterations for each Delay value
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
pulseWidth = 500

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
from setASICconfig_testbeam import set_pixel_parameters        ##
                                                               ##
#################################################################


def acquire_data(top, useExt, DelayRange): 
    pixel_stream = feb.PixelReader()    
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixelData = []
    pulser = top.Fpga[0].Asic.Gpio.DlyCalPulseSet #rising edge of pulser and extTrig

    for delay_value in DelayRange:
        print('Testing delay value ' + str(delay_value) )
        pulser.set(delay_value)
        if useExt:
            top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(delay_value+pulseWidth)


        for pulse_iteration in range(NofIterationsTOA):
            if (asicVersion == 1):
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.01)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)
        pixelData.append( pixel_stream.HitData.copy() )
        while pixel_stream.count < NofIterationsTOA: pass
        pixel_stream.clear()
    return pixelData
#################################################################
def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    
    #default parameters
    pixel_probe = 1
    pixel_min = 0
    pixel_max = 14
    DAC_Vth = 320
    outFile = 'TestData/TOAmeasurement'
    config_file = 'config/testbeam_config.yml' # <= Path to the Configuration File to be Loaded
    ipIN=['192.168.1.10']
    
    
    # Add arguments
    parser.add_argument( "--ip", nargs ='+', required = False, default = ipIN, help = "List of IP addresses")  
    parser.add_argument( "--cfg", required = False, default = config_file, help = "Select yml configuration file to load")  
    parser.add_argument("--refClkSel", type     = str, required = False, default  = 'IntClk', help     = "Selects the reference input clock for the jitter cleaner \PLL: IntClk = on-board OSC, ExtSmaClk = 50 Ohm SMA Clock, ExtLemoClk = 100Ohm diff pair Clock")
    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--pixelProbe", type = int, required = False, default = pixel_probe, help = "pixel for probe readout")
    parser.add_argument("--pixelMin", type = int, required = False, default = pixel_min, help = "first pixel to read out")
    parser.add_argument("--pixelMax", type = int, required = False, default = pixel_max, help = "last pixel to read out")
    # Get the arguments
    args = parser.parse_args()
    return args
#################################################################
def testbeamDAQ(argsip,
      Configuration_LOAD_file,
      refClkSel,
      DAC,
      pixel_probe,
      pixel_min,
      pixel_max):


    # Setup root class
    print("Loading ASIC common configuration ----")
    top = feb.Top(ip = argsip, userYaml = [Configuration_LOAD_file])
    
    if DebugPrint:
        top.Fpga[0].AxiVersion.printStatus()
        # Tap the streaming data interface (same interface that writes to file)
        dataStream = feb.PrintEventReader()    
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

    #do we need this?
    print("Doing RSTB for TDC and DLL ---")
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)

    print("Pixel configuration: probe = ch %d , pixel start = %d, pixel end = %d" % pixel_probe, pixel_min, pixel_max)
    set_pixel_parameters(top, pixel_min, pixel_max, pixel_probe)
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DAC)


    LoopCnt = 0
    
    #open output file, write first lines with run configuration
    #config is a dict! just get it from there :P

    # Data Acquisition
    print("Setting up trigger --- ")
    ## configure trigger here ##
    
    #You MUST call this function after doing ASIC configurations!!!->I am guessing this should be last of all??
    top.initialize()

    #Data taking loop: go up to 4096 events and then write to file
    #should be within a while loop that catches a ctrl+c 
    #ctrl+c should not kill before writing data to file
    #should be possible to set max number of loops

    #pixel_data = acquire_data(top, useExt, DelayRange)



   #################################################################
    # Save Data
    #################################################################

    
    
    if os.path.exists(outFile+'.txt'):
      ts = str(int(time.time()))
      outFile = outFile+ts
    outFile = outFile+'.txt'
    
    ff = open(outFile,'a')
    ff.write('TOA measurement vs Delay ---- '+time.ctime()+'\n')
    if useExt:
        ff.write('Using ext trigger, width = '+str(pulseWidth)+'\n')
    ff.write('Pixel = '+str(pixel_number)+'\n')
    ff.write('config file = '+Configuration_LOAD_file+'\n')
    ff.write('NofIterations = '+str(NofIterationsTOA)+'\n')
    #ff.write('cmd_pulser = '+str(Qinj)+'\n')
    #ff.write('Delay DAC = '+str(DelayValue)+'\n')
    ff.write('LSBest = '+str(LSBest)+'\n')
    #ff.write('Threshold = '+str(DACvalue)+'\n')
    #ff.write('N hits = '+str(sum(HitCnt))+'\n')
    #ff.write('Number of events = '+str(len(HitData))+'\n')
    ff.write('mean value = '+str(DataMean)+'\n')
    ff.write('sigma = '+str(DataStdev)+'\n')
    ff.write('Pulse delay   TOA '+'\n')
    for idel in range(len(DelayRange)):
      pulser = DelayRange[idel]
      for itoa in range(len(allTOAdata[idel])):
        ff.write(str(pulser)+' '+str(allTOAdata[idel][itoa])+'\n')
    #ff.write('TOAvalues = '+str(HitDataTOT)+'\n')
    ff.close()
    
    print('Saved file '+outFile)
 
    time.sleep(0.5)
    # Close
    top.stop()
    #################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)

    testbeamDAQ(args.ip, args.cfg, args.refClkSel)
