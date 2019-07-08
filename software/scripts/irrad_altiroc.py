#!/usr/bin/env python3
#################################################################
#  Run continous measurements during irradiation
#################################################################
import sys
import os
import time
from subprocess import call
import random
import argparse
import pyrogue as pr
import pyrogue.gui
import numpy as np
import common as feb
import rogue.utilities.fileio
import statistics
import math
import matplotlib.pyplot as plt
##########################
from probeMeasurement_B1 import *
from fixedTOAhistogram_B1 import *

from ReaderTools_B1 import *
#################################################################
def main():
  
  scopeDir = '/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/oscilloscope/'
  keithleyDir='/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/Keithley/'
  TDCdir = '/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/TDC/'

  logfile = open('/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/irradlog_'+str(int(time.time()))+'.txt','w')
  logfile.write('=======Starting irradiation measurement=========\n')
  logfile.write(time.ctime()+'\n')

  ########################################
  # Setup root class
  argip = '192.168.1.10'
  configFile = 'config/config_irrad_B1.yml'
  ########################################
  top = feb.Top(hwType='eth',ip = argip)

  # Start the system
  top.start(initRead=True)

  # Load the default YAML file
  print('Loading Configuration File...')
  #top.LoadConfig(arg = configFile)
  #top.Asic.DoutDebug.ForwardData.set(0x0)

  ## Tap the streaming data interface (same interface that writes to file)
  #dataStream = MyEventReader()
  #pyrogue.streamTap(top.dataStream, dataStream)
  ########################################

  while True:
    #list of files created in each loop, to move and analyse at the end
    ch4_scopeData = []
    ch9_scopeData = []
    ch14_scopeData = []

    top.LoadConfig(arg = configFile)
    top.Asic.DoutDebug.ForwardData.set(0x0)

    startTime=time.ctime()
    ts = str(int(time.time()))
    ##########################
    print('Preamp probe measurements  '+startTime)
    logfile.write('Preamp probe measurements  '+startTime+'\n')
    ##########################
    #ch4- Qinj = 5.24fC, Vth@1fC, delay = 50
    ch4_scopeData.append(probeMeasurement(top,argip,configFile,4,6,349,50,True,True))
    #ch4- Qinj = 10.32fC, Vth@1fC, delay = 50                                                
    ch4_scopeData.append(probeMeasurement(top,argip,configFile,4,12,349,50,True,True))

    #????should dump here info on probe amplitude, risetime

    startTime=time.ctime()
    ##########################
    print('Discri probe measurements  '+startTime)
    ##########################
    #ch4- Qinj = 5.24fC, Vth@1fC, delay = 50
    ch4_scopeData.append(probeMeasurement(top,argip,configFile,4,6,349,50,False,True))
    #ch4- Qinj = 10.32fC, Vth@1fC, delay = 50 
    ch4_scopeData.append(probeMeasurement(top,argip,configFile,4,12,349,50,False,True))

    #????should dump here info on jitter
    print(ch4_scopeData)


    ##########################
    #TDC measurements
    ##########################
    # 2k TOA measurements
    outTDC=TDCdir+'ch4/dataTOAch4Q6_'+ts+'.txt'
    ch4TOA = fixedTOAhistogram(top,argip,configFile,4,6,349,50,outTDC)
    #outTDC=TDCdir+'ch4/dataTOAch4Q12_'+ts+'.txt'
    #ch4TOA = fixedTOAhistogram(top,argip,configFile,4,12,349,50,outTDC)
    

    ##########################
    #Keithely readout
    ##########################
    #probeMeasurement(top,argip,configFile,4,6,349,50,False,False)
    #call('python2 readKeithley_irrad.py',shell=True)


#################################################################
if __name__ == "__main__":
    main()

