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

Configuration_LOAD_file = 'config/config_irrad_B1.yml' # <= Path to the Configuration File to be Loaded    config/test_Conso_AllChON.yml

pixel_number = 4        # <= Pixel to be Tested
useProbe = False        #output discri probe

DataAcqusitionTOA = 1   # <= Enable TOA Data Acquisition (Delay Sweep)
minDAC = 360           #threshold scan
maxDAC = 380
DACstep = 1
DelayValueTOA = 0
NofIterationsTOA = 50  # <= Number of Iterations for each Delay value
LSBest = 28.64 #ch4=28.64, ch9=30.4 ch14=31.28 #ps
Qinj = 6  #Mod8.64fied Pulser Decimal code 3 = 2.66,6 = 5.24, 12 =10.32 fC, 24=20.08 fC  ##

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

#################################################################
# Class for Printing Data during Acquisition
class MyEventReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)
        self.lastTOT = 0
        self.printNext = 0
        self.printNextEn = 0
        self.PrintData = 1

    def _acceptFrame(self,frame):
        # Get the payload data
        p = bytearray(frame.getPayload())
        # Return the buffer index
        frame.read(p,0)
        # Check for a modulo of 32-bit word 
        if ((len(p) % 4) == 0):
            count = int(len(p)/4)
            # Combine the byte array into 32-bit word array
            hitWrd = np.frombuffer(p, dtype='uint32', count=count)
            # Loop through each 32-bit word
            for i in range(count):
                # Parse the 32-bit word
                dat = feb.ParseDataWord(hitWrd[i])
                # Print the event if hit
                #if (dat.Hit > 0) or (self.printNext == 1 and self.printNextEn == 1):
                #if (dat.Hit > 0):
                if (dat.Hit > 0) or (self.printNext == 1 and self.printNextEn == 1) or (dat.TotData != 0x1fc and dat.TotData != self.lastTOT):

                    self.lastTOT = dat.TotData

                    if (self.printNext == 1) and (dat.Hit == 0):
                        self.printNext = 0
                    else:
                        self.printNext = 1
            
                    #if (j == 1):
                    #if (self.PrintData == 1) and (j == 1):
                    if not (dat.ToaOverflow == 1 and dat.ToaData != 0x7f) and (self.PrintData == 1) and (j == 1):
                        
                        print( 'Event[SeqCnt=0x%x]: (TotOverflow = %r, TotData = 0x%x), (ToaOverflow = %r, ToaData = 0x%x), hit=%r' % (
                                dat.SeqCnt,
                                dat.TotOverflow,
                                dat.TotData,
                                dat.ToaOverflow,
                                dat.ToaData,
                                dat.Hit,
                        )) 

#################################################################

#################################################################
# Class for Reding the Data from File
class MyFileReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)
        self.HitData = []
        self.HitDataTOTf_vpa = []
        self.HitDataTOTf_tz = []
        self.HitDataTOTc_vpa = []
        self.HitDataTOTc_tz = []
        self.HitDataTOTc_int1_vpa = []
        self.HitDataTOTc_int1_tz = []
        self.HitDataTOTf_vpa_temp = 0
        self.HitDataTOTc_vpa_temp = 0
        self.HitDataTOTf_tz_temp = 0
        self.HitDataTOTc_tz_temp = 0
        self.HitDataTOTc_int1_vpa_temp = 0
        self.HitDataTOTc_int1_tz_temp = 0

    def _acceptFrame(self,frame):
        # Get the payload data
        p = bytearray(frame.getPayload())
        # Return the buffer index
        frame.read(p,0)
        # Check for a modulo of 32-bit word 
        if ((len(p) % 4) == 0):
            count = int(len(p)/4)
            # Combine the byte array into 32-bit word array
            hitWrd = np.frombuffer(p, dtype='uint32', count=count)
            # Loop through each 32-bit word
            for i in range(count):
                # Parse the 32-bit word
                dat = feb.ParseDataWord(hitWrd[i])
                # Print the event if hit

                #if (dat.Hit > 0) and (dat.ToaOverflow == 0):
                if (dat.Hit > 0):
                   
                    self.HitData.append(dat.ToaData)
                
                if (dat.Hit > 0) and (dat.TotData != 0x1fc):
    
                    self.HitDataTOTf_vpa_temp = ((dat.TotData >>  0) & 0x3) + dat.TotOverflow*math.pow(2,2)
                    self.HitDataTOTc_vpa_temp = (dat.TotData >>  2) & 0x7F
                    self.HitDataTOTc_int1_vpa_temp = (((dat.TotData >>  2) + 1) >> 1) & 0x3F
                    #if ((dat.TotData >>  2) & 0x1) == 1:
                    self.HitDataTOTf_vpa.append(self.HitDataTOTf_vpa_temp)
                    self.HitDataTOTc_vpa.append(self.HitDataTOTc_vpa_temp)
                    self.HitDataTOTc_int1_vpa.append(self.HitDataTOTc_int1_vpa_temp)

                if (dat.Hit > 0) and (dat.TotData != 0x1f8):

                    self.HitDataTOTf_tz_temp = ((dat.TotData >>  0) & 0x7) + dat.TotOverflow*math.pow(2,3)
                    self.HitDataTOTc_tz_temp = (dat.TotData >>  3) & 0x3F
                    self.HitDataTOTc_int1_tz_temp = (((dat.TotData >>  3) + 1) >> 1) & 0x1F
                    self.HitDataTOTf_tz.append(self.HitDataTOTf_tz_temp)                    
                    self.HitDataTOTc_tz.append(self.HitDataTOTc_tz_temp)
                    self.HitDataTOTc_int1_tz.append(self.HitDataTOTc_int1_tz_temp)
                   
#################################################################

#################################################################
# Set the argument parser
parser = argparse.ArgumentParser()

# Convert str to bool
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

# Add arguments
parser.add_argument("--ip", type = str, required = True, help = "IP address")  
parser.add_argument("--out", type = str, required = False, default = 'testThreshold.txt', help = "output file name")  

# Get the arguments
args = parser.parse_args()

#################################################################
# Setup root class
top = feb.Top(hwType='eth',ip= args.ip)    

# Start the system
top.start(initRead=True)

# Load the default YAML file
print('Loading Configuration File...')
top.ReadConfig(arg = Configuration_LOAD_file)
top.Asic.DoutDebug.ForwardData.set(0x0)

# Tap the streaming data interface (same interface that writes to file)
dataStream = MyEventReader()    
pyrogue.streamTap(top.dataStream, dataStream) 
#################################################################

#################################################################
# Pixel Readout Selection                                      ##
                                                               ##
if Disable_CustomConfig == 0:                                  ## 
                                                               ##
    top.Asic.Probe.en_probe_pa.set(0x0)                        ##
    #top.Asic.Probe.en_probe_dig.set(0x0)
                                                               ##
    for i in range(25):                                        ##
        top.Asic.Probe.pix[i].probe_pa.set(0x0)                ## 
        top.Asic.Probe.pix[i].probe_vthc.set(0x0)              ## 
        top.Asic.Probe.pix[i].probe_dig_out_disc.set(0x0)      ##
        top.Asic.Probe.pix[i].probe_toa.set(0x0)               ##
        top.Asic.Probe.pix[i].probe_tot.set(0x0)               ##
        top.Asic.Probe.pix[i].totf.set(0x0)                    ##
        top.Asic.Probe.pix[i].tot_overflow.set(0x0)            ##
        top.Asic.Probe.pix[i].toa_busy.set(0x0)                ##
        top.Asic.Probe.pix[i].toa_ready.set(0x0)               ##
        top.Asic.Probe.pix[i].tot_busy.set(0x0)                ##
        top.Asic.Probe.pix[i].tot_ready.set(0x0)               ##
        top.Asic.Probe.pix[i].en_read.set(0x0)                 ##
    
    if not useProbe:
        top.Asic.Probe.en_probe_dig.set(0x0)
                                                           ##
    if pixel_number in range(0, 5):                            ##
        if useProbe:
            top.Asic.Probe.en_probe_dig.set(0x1)                   ## 0x1
        top.Asic.Probe.EN_dout.set(0x1)                        ##
    if pixel_number in range(5, 10):                           ##
        if useProbe:top.Asic.Probe.en_probe_dig.set(0x2)                   ## 0x2
        top.Asic.Probe.EN_dout.set(0x2)                        ##
    if pixel_number in range(10, 15):                          ##
        if useProbe:top.Asic.Probe.en_probe_dig.set(0x4)                   ## 0x4
        top.Asic.Probe.EN_dout.set(0x4)                        ##
    if pixel_number in range(15, 20):                          ##
        if useProbe:top.Asic.Probe.en_probe_dig.set(0x8)                   ## 0x8
        top.Asic.Probe.EN_dout.set(0x8)                        ##
    if pixel_number in range(20, 25):                          ##
        if useProbe:top.Asic.Probe.en_probe_dig.set(0x10)                  ##
        top.Asic.Probe.EN_dout.set(0x10)                       ##
                                                           ##
    top.Asic.Gpio.RSTB_READ.set(0x0)                           ##
    time.sleep(0.1)                                            ##
    top.Asic.Gpio.RSTB_READ.set(0x1)                           ##
    
    if useProbe:                                                           ##
        top.Asic.Probe.pix[pixel_number].probe_pa.set(0x0)         ## 
        top.Asic.Probe.pix[pixel_number].probe_vthc.set(0x0)       ## 
        top.Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x1)#
        top.Asic.Probe.pix[pixel_number].probe_toa.set(0x0)        ##
        top.Asic.Probe.pix[pixel_number].probe_tot.set(0x0)        ##
        top.Asic.Probe.pix[pixel_number].totf.set(0x0)             ##
        top.Asic.Probe.pix[pixel_number].tot_overflow.set(0x0)     ##
        top.Asic.Probe.pix[pixel_number].toa_busy.set(0x0)         ##
        top.Asic.Probe.pix[pixel_number].toa_ready.set(0x0)        ##
        top.Asic.Probe.pix[pixel_number].tot_busy.set(0x0)         ##
        top.Asic.Probe.pix[pixel_number].tot_ready.set(0x0)        ##

    top.Asic.Probe.pix[pixel_number].en_read.set(0x1)          ##
#################################################################

#################################################################
# Custom Configuration                                         ##
                                                               ##
if Disable_CustomConfig == 0:                                  ##
                                                               ##
    for i in range(25):                                        ##
        top.Asic.SlowControl.disable_pa[i].set(0x1)            ##
        top.Asic.SlowControl.ON_discri[i].set(0x0)             ##
        top.Asic.SlowControl.EN_ck_SRAM[i].set(0x1)            ##
        top.Asic.SlowControl.EN_trig_ext[i].set(0x0)           ##
        top.Asic.SlowControl.ON_Ctest[i].set(0x0)              ##
                                                               ##
        top.Asic.SlowControl.cBit_f_TOA[i].set(0x0)            ##
        top.Asic.SlowControl.cBit_s_TOA[i].set(0x0)            ##      
        top.Asic.SlowControl.cBit_f_TOT[i].set(0x0)            ##
        top.Asic.SlowControl.cBit_s_TOT[i].set(0x0)            ##
        top.Asic.SlowControl.cBit_c_TOT[i].set(0x0)            ##
                                                               ##
    for i in range(16):                                        ##
        top.Asic.SlowControl.EN_trig_ext[i].set(0x0)           ##
                                                               ##
    top.Asic.SlowControl.disable_pa[pixel_number].set(0x0)     ##
    top.Asic.SlowControl.ON_discri[pixel_number].set(0x1)      ##
    top.Asic.SlowControl.EN_hyst[pixel_number].set(0x1)        ##
    top.Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)    ##
    top.Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)     ##
    top.Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)       ##
    ##top.Asic.SlowControl.bit_vth_cor[pixel_number].set(0x40)   ##
                                                               ##
    top.Asic.SlowControl.Write_opt.set(0x0)                    ##
    top.Asic.SlowControl.Precharge_opt.set(0x0)                ##
                                                               ##
    top.Asic.SlowControl.DLL_ALockR_en.set(0x1)                ##
    top.Asic.SlowControl.CP_b.set(0x5) #5                      ##
    top.Asic.SlowControl.ext_Vcrtlf_en.set(0x0) #1             ##
    top.Asic.SlowControl.ext_Vcrtls_en.set(0x0) #1             ##
    top.Asic.SlowControl.ext_Vcrtlc_en.set(0x0) #1             ##
                                                               ##
    top.Asic.SlowControl.totf_satovfw.set(0x1)                 ##
    top.Asic.SlowControl.totc_satovfw.set(0x1)                 ##
    top.Asic.SlowControl.toa_satovfw.set(0x1)                  ##
                                                               ##
    top.Asic.SlowControl.SatFVa.set(0x3)                       ##
    top.Asic.SlowControl.IntFVa.set(0x1)                       ##
    top.Asic.SlowControl.SatFTz.set(0x4)                       ##
    top.Asic.SlowControl.IntFTz.set(0x1)                       ##
                                                               ##
    top.Asic.SlowControl.cBitf.set(0x0) #0                     ##
    top.Asic.SlowControl.cBits.set(0xf) #f                     ##
    top.Asic.SlowControl.cBitc.set(0xf) #f                     ##
                                                               ##
    top.Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0) #f  ##
    top.Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0) #0  ##
                                                               ##
    top.Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf) #f  ##
    top.Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0) #0  ##
    top.Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf) #0  ##
                                                               ##
    top.Asic.SlowControl.Rin_Vpa.set(0x0) #0                   ##
    top.Asic.SlowControl.Cp_Vpa.set(0x0) #0                    ##
    top.Asic.SlowControl.cd[0].set(0x7) #6                     ## DON'T FORGET to change cd [] 0, 1 or 2 for ch4, 9 or 14
    top.Asic.SlowControl.cd[1].set(0x7) #6                     ## DON'T FORGET to change cd [] 0, 1 or 2 for ch4, 9 or 14
    top.Asic.SlowControl.cd[2].set(0x7) #6                     ## DON'T FORGET to change cd [] 0, 1 or 2 for ch4, 9 or 14
    top.Asic.SlowControl.dac_biaspa.set(30) #10 30= 0x1e 60=0x3c ##
    top.Asic.SlowControl.dac_pulser.set(Qinj) # Modified Pulser Decimal code 3 = 2.66,6 = 5.24, 12 =10.32 fC, 24=20.08 fC  ##
    top.Asic.SlowControl.DAC10bit.set(398)           ##
    top.SysReg.DlyData.set(DelayValueTOA)
                                                           ##
    top.Asic.DoutDebug.DeserSampleEdge.set(0x0)                ##
                                                               ##
    top.Asic.PulseTrain.PulseCount.set(0x1)                    ## 0X1
    top.Asic.PulseTrain.PulseWidth.set(0x8)                    ## 0X8
    top.Asic.PulseTrain.PulsePeriod.set(0x4)                   ## 0X4
    top.Asic.PulseTrain.PulseDelay.set(0x4)                    ## 0X4
    top.Asic.PulseTrain.ReadDelay.set(0x9)                     ## 0X8
    top.Asic.PulseTrain.ReadDuration.set(0x70) #10a0           ## 0X70
    top.Asic.PulseTrain.ResetCounterMask.set(0x3)              ## 0X3
    top.Asic.PulseTrain.ResetTdcMask.set(0x2)                  ## 0X2
                                                               ##
#################################################################

#################################################################
# Data Stream Alignment                                        ##
                                                               ##
top.Asic.PulseTrain.Continuous.set(0x0)                        ##
top.Asic.Gpio.RSTB_TDC.set(0x0)                                ##
Write_opt = top.Asic.SlowControl.Write_opt.get()               ##
Precharge_opt = top.Asic.SlowControl.Precharge_opt.get()       ##  
top.Asic.SlowControl.Write_opt.set(0x0)                        ##
top.Asic.SlowControl.Precharge_opt.set(0x0)                    ##
time.sleep(0.1)                                                ##
top.Asic.PulseTrain.ResetCounterPolarity.set(0x1)              ##
top.Asic.PulseTrain.Continuous.set(0x1)                        ##
time.sleep(0.1)                                                ##
top.Asic.SlowControl.Write_opt.set(Write_opt)                  ##
top.Asic.SlowControl.Precharge_opt.set(Precharge_opt)          ##
top.Asic.Gpio.RSTB_TDC.set(0x1)                                ##
top.Asic.PulseTrain.ResetCounterPolarity.set(0x0)              ##
top.Asic.PulseTrain.Continuous.set(0x0)                        ##
time.sleep(0.1)                                                ##
#################################################################

#################################################################
# Data Acquisition                                             ##
# vs threshold                                                 ##
dacScan = []                                                   ##
                                                               ##
for i in range(minDAC,maxDAC,DACstep):                         ##
                                                               ##
    print ('ThresholdDAC =',i)                                 ##
    dacScan.append(i)                                          ##
    top.Asic.SlowControl.DAC10bit.set(i) #350                  ##
    ##align data after each thr setting?                       ##
                                                               ##
    try:                                                       ##
        os.remove('TestData/test_th%d.dat' %i)                 ##
    except OSError:                                            ##
        pass                                                   ##
    top.dataWriter._writer.open('TestData/test_th%d.dat' %i)   ##
    top.Asic.DoutDebug.ForwardData.set(0x1)                    ##
    time.sleep(0.1)
    for j in range(NofIterationsTOA):                          ##
                                                               ##
        top.Asic.Gpio.RSTB_TDC.set(0x0)                        ##
        top.Asic.Gpio.RSTB_TDC.set(0x1)                        ##
        time.sleep(0.01)                                       ##
        top.Asic.PulseTrain.OneShot()                          ##
                                                               ##
    top.Asic.DoutDebug.ForwardData.set(0x0)                    ##
    top.dataWriter._writer.close()                             ##
                                                               ##
#################################################################

#################################################################
# Data Processing

thr_DAC = []
HitCnt = []
TOAmean = []
TOAjit = []
TOAmean_ps = []
TOAjit_ps = []

for i in dacScan:
    # Create the File reader streaming interface
    dataReader = rogue.utilities.fileio.StreamReader()
    time.sleep(0.01)
    # Create the Event reader streaming interface
    dataStream = MyFileReader()
    time.sleep(0.01)
    # Connect the file reader to the event reader
    pr.streamConnect(dataReader, dataStream) 
    time.sleep(0.01)
    # Open the file
    dataReader.open('TestData/test_th%d.dat' %i)
    time.sleep(0.01)
    # Close file once everything processed
    dataReader.closeWait()
    time.sleep(0.01)

    try:
        print('Processing Data for THR DAC = %d...' % i)
    except OSError:
        pass 

    HitData = dataStream.HitData

    thr_DAC.append(i)
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
    try:
        print('Threshold = %d, HitCnt = %d/%d' % (dacScan[i], HitCnt[i], NofIterationsTOA))
    except OSError:
        pass
    if HitCnt[i] == NofIterationsTOA:
        if i>0 and HitCnt[i-1] > NofIterationsTOA :
            minTH = (dacScan[i-1]+dacScan[i])/2
        elif i<len(dacScan)-1 and HitCnt[i+1] < NofIterationsTOA :
            maxTH = (dacScan[i+1]+dacScan[i])/2
    if HitCnt[i]/NofIterationsTOA < 0.6:
        th50percent = dacScan[i]

th25= (maxTH-minTH)*0.25+minTH
th50= (maxTH-minTH)*0.5+minTH
th75= (maxTH-minTH)*0.75+minTH
print('Found minTH = %d, maxTH = %d  - points at 0.25, 0.50 and 0.75 are %d,%d,%d'% (minTH,maxTH,th25,th50,th75))
print('First DAC with efficiency below 60% = ', th50percent)
ff = open(args.out,'a')
ff.write('Threshold scan ----'+time.ctime()+'\n')
ff.write('Pixel = '+str(pixel_number)+'\n')
#ff.write('column = '+hex(column)+'\n')
ff.write('config file = '+Configuration_LOAD_file+'\n')
ff.write('NofIterationsTOA = '+str(NofIterationsTOA)+'\n')
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
ff.write('\n')
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
