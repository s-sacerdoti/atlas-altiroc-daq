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
from setASICconfig_v2B7 import *
from setASICconfig_v2B8 import *
#################################################################
#script settings
LSBest = 20
NofIterations = 20  # <= Number of Iterations for each Vth
useProbe = False        #output discri probe
DebugPrint = True
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
    parser.add_argument("--ip", nargs ='+', required = False, default = ['192.168.1.10'], help = "List of IP address")
    parser.add_argument( "--board", type = int, required = False, default = 7,help = "Choose board")
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
def acquire_data(top, dac_list,asic_pulser): 
    
    pixel_stream = feb.PixelReader()
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixelData = []
    asicVersion = 1 #hardcoded for now...

    for i in dac_list:
        print('Vth DAC = %d' %i) 
        top.Fpga[0].Asic.SlowControl.DAC10bit.set(i)
    
        for j in range(NofIterations):
            if (asicVersion == 1): 
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.05)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)
        pixelData.append( pixel_stream.HitData.copy() )
        while pixel_stream.count < NofIterations: pass
        pixel_stream.clear()
    
    return pixelData

#################################################################
#################################################################
def thresholdScan(argip,
      board,
      Configuration_LOAD_file,
      pixel_number,
      Qinj,
      DelayValue,
      minDAC,
      maxDAC,
      DACstep,
      outFile):

  dacScan = range(minDAC,maxDAC,DACstep)
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
  if board == 7:
    set_fpga_for_custom_config_B7(top,pixel_number)
  elif board == 8:
    set_fpga_for_custom_config_B8(top,pixel_number)
  #some more config
  top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(DelayValue)
  top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj)
  
  #Take data
  pixel_data = acquire_data(top, dacScan,
             top.Fpga[0].Asic.Gpio.DlyCalPulseSet)
  
  #################################################################
  # Data Processing
  
  HitCnt = []
  TOAmean = []
  TOAjit = []
  TOAmean_ps = []
  TOAjit_ps = []
  allTOA = []

  num_valid_TOA_reads = len(pixel_data)
  if num_valid_TOA_reads == 0:
      raise ValueError('No hits were detected during delay sweep. Aborting!')
  
  for idac,dacval in enumerate(dacScan):
      
      HitData = pixel_data[idac]
      HitCnt.append(len(HitData))
      allTOA.append(HitData)

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

      # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
      index = np.where(np.sort(TOAjit))
      if len(index)>1:
        jitterMean = np.mean(np.sort(TOAjit)[index[0][0]:len(np.sort(TOAjit))])
      else:
        jitterMean = 0
   
  #################################################################
  
  #################################################################
  # Print Data
  #find min th, max th, and middle points:
  minTH = 0.
  maxTH = 1024.
  th50percent = 1024.
  
  midPt = []
  for i in range(len(dacScan)):
      try:
          print('Threshold = %d, HitCnt = %d/%d' % (dacScan[i], HitCnt[i], NofIterations))
      except OSError:
          pass
      if HitCnt[i] > NofIterations-2:
          if i>0 and HitCnt[i-1] < (NofIterations-1) :
              minTH = (dacScan[i-1]+dacScan[i])/2
          elif i<len(dacScan)-1 and HitCnt[i+1] < NofIterations :
              maxTH = (dacScan[i+1]+dacScan[i])/2
      if HitCnt[i]/NofIterations < 0.6:
          th50percent = dacScan[i]
  
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
  for iTh in range(len(dacScan)):
      vth = dacScan[iTh]
      for itoa in range(len(allTOA[iTh])):
          ff.write(str(vth)+' '+str(allTOA[iTh][itoa])+' '+str(len(allTOA[iTh]))+'\n')

  ff.close()
  
  #################################################################
  #################################################################
  ## Plot Data
  fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))
  
  #plot N events vs threshold
  ax1.plot(dacScan,HitCnt)
  #ax1.scatter(dacScan,HitCnt)
  ax1.set_title('Number of hits vs Threshold', fontsize = 11)
  ax1.set_xlabel('Threshold DAC', fontsize = 10)
  ax1.set_ylabel('Number of TOA hits', fontsize = 10)
  
  #plot TOA vs threshold
  ax2.scatter(dacScan,TOAmean_ps)
  ax2.set_title('Mean TOA vs Threshold', fontsize = 11)
  ax2.set_xlabel('Threshold DAC', fontsize = 10)
  ax2.set_ylabel('Mean TOA value [ps]', fontsize = 10)
  
  #plot jitter vs Threshold
  ax3.scatter(dacScan,TOAjit_ps)
  ax3.set_title('Jitter TOA vs Threshold', fontsize = 11)
  ax3.legend(['Average Std. Dev. = %f ps' % (jitterMean*LSBest)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
  ax3.set_xlabel('Threshold DAC', fontsize = 10)
  ax3.set_ylabel('Mean TOA Jitter', fontsize = 10)
  
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
    thresholdScan(args.ip, args.board, args.cfg, args.ch, args.Q,args.delay, args.minVth, args.maxVth, args.VthStep, args.out)

