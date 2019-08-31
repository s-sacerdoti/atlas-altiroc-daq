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
#from setASICconfig_v2B8 import *
from setASICconfig_v2B7 import *
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
    
    fileList = []
    asicVersion = 1 # <= Select either V1 or V2 of the ASIC

    for i in range(range_low, range_high, range_step):
        print(file_prefix+'step = %d' %i) 
        asic_pulser.set(i)
    
        ts = str(int(time.time()))
        val = '%d_' %i
        filename = 'TestData/'+file_prefix+val+ts+'.dat'
        try: os.remove(filename)
        except OSError: pass

        top.dataWriter._writer.open(filename)
        fileList.append(filename)

        for j in range(n_iterations):
            if (asicVersion == 1): 
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.01)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)

        while dataStream.count < n_iterations: pass
        top.dataWriter._writer.close()
        dataStream.count = 0 
    
    return fileList

#################################################################
#################################################################
def timewalk(argip,
      Configuration_LOAD_file,
      pixel_number,
      Vth,
      DelayValue,
      minPulser,
      maxPulser,
      PulserStep,
      outFile):

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
  set_fpga_for_custom_config(top, pixel_number)
  #some more config
  top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(DelayValue)
  top.Fpga[0].Asic.SlowControl.DAC10bit.set(Vth)
  
  #Take data
  fileList = acquire_data(minPulser, maxPulser, PulserStep, top,
             top.Fpga[0].Asic.SlowControl.dac_pulser, 'TW', NofIterations, dataStream)
  
  #################################################################
  # Data Processing
  
  ValidTOACnt = []
  ValidTOTCnt = []
  TOAmean = []
  TOTmean = []
  TOAjit = []
  TOTjit = []
  TOAmean_ps = []
  TOAjit_ps = []
  allTOAdata = []
  allTOTdata = []
  HitDataTOTf_cumulative = []
  
  for ipuls in range(len(pulser_list)):
      fileName = fileList[ipuls]
      pulser = pulser_list[ipuls]
      # Create the File reader streaming interface
      dataReader = rogue.utilities.fileio.StreamReader()
      
      # Create the Event reader streaming interface
      dataStream = feb.MyFileReader()
      
      # Connect the file reader to the event reader
      pr.streamConnect(dataReader, dataStream) 
      
      # Open the file
      dataReader.open(fileName)
      
      # Close file once everything processed
      dataReader.closeWait()
  
      try:
          print('Processing Data for Qinj DAC = %d...' % pulser)
      except OSError:
          pass 
  
      HitDataTOA = dataStream.HitData
      HitDataTOT = dataStream.HitDataTOT
      allTOAdata.append(HitDataTOA)
      allTOTdata.append(HitDataTOT)
      HitDataTOTf = dataStream.HitDataTOTf_vpa
      HitDataTOTc = dataStream.HitDataTOTc_vpa
      HitDataTOTc_int1 = dataStream.HitDataTOTc_int1_vpa
      HitDataTOTf_cumulative = HitDataTOTf_cumulative + dataStream.HitDataTOTf_vpa
  
      ValidTOACnt.append(len(HitDataTOA))
      ValidTOTCnt.append(len(HitDataTOT))
      if len(HitDataTOTf) > 0:
          list((np.asarray(HitDataTOTc) + 1)*LSB_TOTc - np.asarray(HitDataTOTf)*LSB_TOTf)

      if len(HitDataTOA) > 0:
          TOAmean.append(np.mean(HitDataTOA, dtype=np.float64))
          TOAjit.append(math.sqrt(math.pow(np.std(HitDataTOA, dtype=np.float64),2)+1/12))
          TOAmean_ps.append(np.mean(HitDataTOA, dtype=np.float64)*LSBest)
          TOAjit_ps.append(math.sqrt(math.pow(np.std(HitDataTOA, dtype=np.float64),2)+1/12)*LSBest)
          if len(HitDataTOT) > 0:
              TOTmean.append(np.mean(HitDataTOT, dtype=np.float64))
              TOTjit.append(math.sqrt(math.pow(np.std(HitDataTOT, dtype=np.float64),2) + math.pow(LSB_TOTf,2)/12))
      else:
          TOAmean.append(0)
          TOAjit.append(0)
          TOAmean_ps.append(0)
          TOAjit_ps.append(0)
          TOTmean.append(0)
          TOTjit.append(0)
      
  #################################################################
  
  #################################################################
  # Print Data
  #find min th, max th, and middle points:
  #minTH = 0.
  #maxTH = 1024.
  #th50percent = 1024.
  
  
  #ff = open(outFile,'a')
  #ff.write('Threshold scan ----'+time.ctime()+'\n')
  #ff.write('Pixel = '+str(pixel_number)+'\n')
  ##ff.write('column = '+hex(column)+'\n')
  #ff.write('config file = '+Configuration_LOAD_file+'\n')
  #ff.write('NofIterations = '+str(NofIterations)+'\n')
  ##ff.write('dac_biaspa = '+hex(dac_biaspa)+'\n')
  #ff.write('DAC Vth = '+str(Vth)+'\n')
  #ff.write('LSBest = '+str(LSBest)+'\n')
  ##ff.write('Cd ='+str(cd*0.5)+' fC'+'\n')
  #ff.write('Found minTH = %d, maxTH = %d - points at 0.25, 0.50 and 0.75 are %d,%d,%d \n'% (minTH,maxTH,th25,th50,th75))
  #ff.write('First DAC with efficiency below 0.6 = %d  \n' % (th50percent))
  #ff.write('Threshold = '+str(pulser_list)+'\n')
  #ff.write('N hits = '+str(ValidTOACnt)+'\n')
  #ff.write('Mean TOA = '+str(TOAmean)+'\n')
  #ff.write('Std Dev TOA = '+str(TOAjit)+'\n')
  #ff.write('MeanTOAps = '+str(TOAmean_ps)+'\n')
  #ff.write('StdDevTOAps = '+str(TOAjit_ps)+'\n')
  #ff.write('dacVth   TOA N_TOA'+'\n')
  #for iTh in range(len(pulser_list)):
  #    vth = pulser_list[iTh]
  #    for itoa in range(len(allTOAdata[iTh])):
  #        ff.write(str(vth)+' '+str(allTOAdata[iTh][itoa])+' '+str(len(allTOAdata[iTh]))+'\n')

  #ff.close()
  
  #################################################################
  #################################################################
  ## Plot Data
  fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))
  
  #plot N events vs threshold
  ax1.scatter(pulser_list,TOAmean)
  #ax1.scatter(pulser_list,ValidTOACnt)
  ax1.set_title('Mean TOA vs Qinj', fontsize = 11)
  
  #plot TOA vs threshold
  ax2.scatter(pulser_list,TOTmean)
  ax2.set_title('Mean TOT vs Qinj', fontsize = 11)
  
  #plot jitter vs Threshold
  ax3.scatter(TOTmean,TOAmean)
  ax3.set_title('Mean TOA vs Mean TOT', fontsize = 11)
  
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
    timewalk(args.ip, args.cfg, args.ch, args.Vth,args.delay, args.minQ, args.maxQ, args.Qstep, args.out)

