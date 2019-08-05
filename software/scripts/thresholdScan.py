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
#from setASICconfig_v2B8 import *
#from setASICconfig_v2B7 import *
from setASICconfig_v2B6 import *
#################################################################
# Set the argument parser
def parse_arguments():
    parser = argparse.ArgumentParser()

    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

    #default parameters
    pixel = 4
    DAC_Vth = 320
    Qinj = 13 #10fc
    config_file = 'config/config_v2B6_noPAprobe.yml'
    minDAC = 280
    maxDAC = 420
    DACstep = 5
    DelayValue = 2400


    # Add arguments
    parser.add_argument("--ip", nargs ='+', required = True, help = "List of IP address")
    parser.add_argument("--cfg", type = str, required = False, default = config_file, help = "config file")
    parser.add_argument("--ch", type = int, required = False, default = pixel, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = Qinj, help = "injected charge DAC")
    parser.add_argument("--delay", type = int, required = False, default = DelayValue, help = "delay")
    parser.add_argument("--minVth", type = int, required = False, default = minDAC, help = "scan start")
    parser.add_argument("--maxVth", type = int, required = False, default = maxDAC, help = "scan stop")
    parser.add_argument("--VthStep", type = int, required = False, default = DACstep, help = "scan step")
    parser.add_argument("--out", type = str, required = False, default = 'testThreshold.txt', help = "output file name")  

    # Get the arguments
    args = parser.parse_args()
    return args

##############################################################################
##############################################################################
def acquire_data(dacScan, top, n_iterations): 
    pixel_stream = feb.PixelReader()    
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixel_data = []
    
    asicVersion = 1 # <= Select either V1 or V2 of the ASIC

    for scan_value in dacScan:
        top.Fpga[0].Asic.SlowControl.DAC10bit.set(i)
    
        for iteration in range(n_iterations):
            if (asicVersion == 1): 
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.01)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)


        pixel_data.append( pixel_stream.HitData )
        while pixel_stream.count < n_iterations: pass
        pixel_stream.clear()
    return pixel_data
#################################################################
#################################################################
def thresholdScan(argip,
      Configuration_LOAD_file,
      pixel_number,
      Qinj,
      DelayValue,
      minDAC,
      maxDAC,
      DACstep,
      outFile):

  LSBest = 20
  NofIterations = 20  # <= Number of Iterations for each Vth
  useProbe = False        #output discri probe
  dacScan = range(minDAC,maxDAC,DACstep)
  DebugPrint = True
  # Setup root class
  top = feb.Top(ip=argip)    
  
  # Load the default YAML file
  print(f'Loading {Configuration_LOAD_file} Configuration File...')
  top.LoadConfig(arg = Configuration_LOAD_file)
  
  if DebugPrint:
      # Tap the streaming data interface (same interface that writes to file)
      dataStream = feb.MyEventReader()    
      pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA
  
  # Custom Configuration
  set_fpga_for_custom_config(top, pixel_number)
  #some more config
  top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(DelayValue)
  top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj)
  
  #Take data
  pixel_data = acquire_data(dacScan, top, NofIterations)
  
  #################################################################
  # Data Processing
  HitCnt = []
  TOAmean = []
  TOAjit = []
  TOAmean_ps = []
  TOAjit_ps = []
  allTOA = []
  
  for dac_index, dac_value in enumerate(dacScan):
      print('Processing Data for THR DAC = %d...' % dac_value)
  
      HitData = dataStream.HitData
      allTOA.append(HitData)
  
      HitCnt.append(len(HitData))
      if len(HitData) > 0:
          TOAmean.append(np.mean(HitData, dtype=np.float64))
          TOAjit.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12))
          TOAmean_ps.append(np.mean(HitData, dtype=np.float64)*LSBest)
          TOAjit_ps.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12)*LSBest)
  
      else:
          TOAmean.append(0)
          TOAjit.append(0)
          TOAmean_ps.append(0)
          TOAjit_ps.append(0)
   
  #################################################################
  
  #################################################################
  # Print Data
  #find min th, max th, and middle points:
  minTH = 0.
  maxTH = 1024.
  th50percent = 1024.
  
  midPt = []
  for i in range(len(dacScan)):
  for dac_index, dac_value in enumerate(dacScan):
      try:
          print('Threshold = %d, HitCnt = %d/%d' % (dac_value, HitCnt[dac_index], NofIterations))
      except OSError:
          pass
      if HitCnt[dac_index] > NofIterations-2:
          if dac_index>0 and HitCnt[dac_index-1] < (NofIterations-1) :
              minTH = (dacScan[dac_index-1]+dacScan[dac_index])/2
          elif i<len(dacScan)-1 and HitCnt[dac_index+1] < NofIterations :
              maxTH = (dacScan[dac_index+1]+dacScan[dac_index])/2
      if HitCnt[dac_index]/NofIterations < 0.6:
          th50percent = dac_value
  
  th25= (maxTH-minTH)*0.25+minTH
  th50= (maxTH-minTH)*0.5+minTH
  th75= (maxTH-minTH)*0.75+minTH
  print('Found minTH = %d, maxTH = %d  - points at 0.25, 0.50 and 0.75 are %d,%d,%d'% (minTH,maxTH,th25,th50,th75))
  print('First DAC with efficiency below 60% = ', th50percent)
  ff = open(outFile,'a')
  ff.write('Threshold scan ----'+time.ctime()+'\n')
  ff.write('Pixel = '+str(pixel_number)+'\n')
  #ff.write('column = '+hex(column)+'\n')
  ff.write('config file = '+Configuration_LOAD_file+'\n')
  ff.write('NofIterations = '+str(NofIterations)+'\n')
  #ff.write('dac_biaspa = '+hex(dac_biaspa)+'\n')
  ff.write('cmd_pulser = '+str(Qinj)+'\n')
  ff.write('LSBest = '+str(LSBest)+'\n')
  #ff.write('Cd ='+str(cd*0.5)+' fC'+'\n')
  ff.write('Found minTH = %d, maxTH = %d - points at 0.25, 0.50 and 0.75 are %d,%d,%d \n'% (minTH,maxTH,th25,th50,th75))
  ff.write('First DAC with efficiency below 0.6 = %d  \n' % (th50percent))
  ff.write('Threshold = '+str(dacScan)+'\n')
  ff.write('N hits = '+str(HitCnt)+'\n')
  ff.write('Mean TOA = '+str(TOAmean)+'\n')
  ff.write('Std Dev TOA = '+str(TOAjit)+'\n')
  ff.write('MeanTOAps = '+str(TOAmean_ps)+'\n')
  ff.write('StdDevTOAps = '+str(TOAjit_ps)+'\n')
  ff.write('dacVth   TOA N_TOA'+'\n')
  for dac_index, dac_value in enumerate(dacScan):
      for itoa in range(len(allTOA[dac_index])):
          ff.write(str(dac_value)+' '+str(allTOA[dac_index][itoa])+' '+str(len(allTOA[dac_index]))+'\n')

  ff.close()
  
  #################################################################
  #################################################################
  ## Plot Data
  fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))
  
  #plot N events vs threshold
  ax1.plot(dacScan,HitCnt)
  #ax1.scatter(dacScan,HitCnt)
  ax1.set_title('Number of hits vs Threshold', fontsize = 11)
  
  #plot TOA vs threshold
  ax2.scatter(dacScan,TOAmean_ps)
  ax2.set_title('Mean TOA vs Threshold', fontsize = 11)
  
  #plot jitter vs Threshold
  ax3.scatter(dacScan,TOAjit_ps)
  ax3.set_title('Jitter TOA vs Threshold', fontsize = 11)
  
  plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
  plt.show()
  #################################################################
  
  time.sleep(0.5)
  # Close
  top.stop()

#################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)
    thresholdScan(args.ip, args.cfg, args.ch, args.Q,args.delay, args.minVth, args.maxVth, args.VthStep, args.out)

