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

asicVersion = 2 # <= Select either V1 or V2 of the ASIC

DebugPrint = True

if (asicVersion == 1):
    Configuration_LOAD_file = 'config/testBojanV1.yml' # <= Path to the Configuration File to be Loaded
else:
    Configuration_LOAD_file = 'config/testBojanV2.yml' # <= Path to the Configuration File to be Loaded

pixel_number = 3 # <= Pixel to be Tested

DataAcqusitionTOA = 0   # <= Enable TOA Data Acquisition (Delay Sweep)
#DelayRange = 251        # <= Range of Programmable Delay Sweep 
DelayRange_low = 2300     # <= low end of Programmable Delay Sweep
DelayRange_high = 2700     # <= high end of Programmable Delay Sweep
DelayRange_step = 1     # <= step size Programmable Delay Sweep
#DelayRange = 11        # <= Range of Programmable Delay Sweep 
NofIterationsTOA = 16  # <= Number of Iterations for each Delay value

DataAcqusitionTOT = 0   # <= Enable TOT Data Acquisition (Pulser Sweep)
PulserRangeL = 800        # <= Low Value of Pulser Sweep Range
PulserRangeH = 2850       # <= High Value of Pulser Sweep Range
PulserRangeStep = 1     # <= Step Size of Pulser Sweep Range
NofIterationsTOT = 16   # <= Number of Iterations for each Pulser Value
DelayValueTOT = 3000       # <= Value of Programmable Delay for TOT Pulser Sweep

nTOA_TOT_Processing = 1 # <= Selects the Data to be Processed and Plotted (0 = TOA, 1 = TOT) 

TOT_f_Calibration_En = 0                                       	   # <= Enables Calculation of TOT Fine-Interpolation Calibration Data and Saves them
#TOT_f_Calibration_LOAD_file = 'TestData/TOT_fine_nocalibration.txt'
TOT_c_Calibration_LOAD_file = 'TestData/TOT_coarse_calibration.txt'  # <= Path to the TOT Coarse Calibration File used in TOT Data Processing
TOT_c_Calibration_SAVE_file = 'TestData/TOT_coarse_calibration.txt'  # <= Path to the File where TOT Coarse Calibration Data are Saved
TOT_f_Calibration_LOAD_file = 'TestData/TOT_fine_calibration.txt'  # <= Path to the TOT Fine-Interpolation Calibration File used in TOT Data Processing
TOT_f_Calibration_SAVE_file = 'TestData/TOT_fine_calibration.txt'  # <= Path to the File where TOT Fine-Interpolation Calibration Data are Saved

DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
LSB_TOTc = 190    # <= Estimate of TOT coarse LSB in ps
LSB_TOTc = 160
LSB_TOTc = 1

nVPA_TZ = 0 # <= TOT TDC Processing Selection (0 = VPA TOT, 1 = TZ TOT) (!) Warning: TZ TOT not yet tested

HistDelayTOA1 = 2425  # <= Delay Value for Histogram to be plotted in Plot (1,0)
HistDelayTOA2 = 2550 # <= Delay Value for Histogram to be plotted in Plot (1,1)
HistDelayTOT1 = 1750  # <= TOT Delay Value for Histogram to be plotted in Plot (1,0)
HistDelayTOT2 = 2750  # <= TOT Delay Value for Histogram to be plotted in Plot (1,1)

TOTf_hist = 0
TOTc_hist = 0
Plot_TOTf_lin = 1
Plot_TOTf_lin_all = 0
PlotValidCnt = 1

##############################################################################

import sys
import rogue
import time
import random
import argparse

import pyrogue as pr
import pyrogue.gui
import numpy as np
import common as feb

import os
import rogue.utilities.fileio

import statistics
import math
import matplotlib.pyplot as plt

##############################################################################

def acquire_data(range_low, range_high, range_step, top, 
        asic_pulser, file_prefix, n_iterations, dataStream): 

    # # dump the configuration (for debugging purposes)
    # top.SaveConfig('test_Bojan_dump.yml')

    for i in range(range_low, range_high, range_step):
        print(file_prefix+'step = %d' %i)
        asic_pulser.set(i)

        filename = 'TestData/'+file_prefix+'%d.dat' %i
        try: os.remove(filename)
        except OSError: pass

        top.dataWriter._writer.open(filename)

        for j in range(n_iterations):
            if (asicVersion == 1):
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.001)
            else:
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                #top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)

        while dataStream.count < n_iterations: pass
        top.dataWriter._writer.close()
        dataStream.count = 0
#################################################################

def get_sweep_index(sweep_value, sweep_low, sweep_high, sweep_step):
    if sweep_value < sweep_low or sweep_high < sweep_value:
        raise ValueError( 'Sweep value {} outside of sweep range [{}:{}]'.format(sweep_value, sweep_low, sweep_high) )
    if sweep_value % sweep_step != 0:
        raise ValueError( 'Sweep value {} is not a multiple of sweep step {}'.format(sweep_value, sweep_step) )
    return int ( (sweep_value - sweep_low) / sweep_step )

#################################################################
# Set the argument parser
parser = argparse.ArgumentParser()

HistDelayTOA1_index  = get_sweep_index(HistDelayTOA1 , DelayRange_low, DelayRange_high, DelayRange_step)
HistDelayTOA2_index  = get_sweep_index(HistDelayTOA2 , DelayRange_low, DelayRange_high, DelayRange_step)
HistDelayTOT1_index = get_sweep_index(HistDelayTOT1, PulserRangeL, PulserRangeH, PulserRangeStep)
HistDelayTOT2_index = get_sweep_index(HistDelayTOT2, PulserRangeL, PulserRangeH, PulserRangeStep)


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

#################################################################
# Setup root class
top = feb.Top(
    ip       = args.ip,
    userYaml = [Configuration_LOAD_file],
    )    

if DebugPrint:
    top.Fpga[0].AxiVersion.printStatus()
    # Tap the streaming data interface (same interface that writes to file)
    dataStream = feb.PrintEventReader()    
    pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

#top.Fpga[0].Asic.SlowControl.ext_Vcrtls_en.set(0x0)

top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
time.sleep(0.1)
top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)
top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)
time.sleep(0.1)

# Data Acquisition for TOA and TOT
if DataAcqusitionTOA == 1:
    acquire_data(DelayRange_low, DelayRange_high, DelayRange_step, top,
            top.Fpga[0].Asic.Gpio.DlyCalPulseSet, 'TOA', NofIterationsTOA, dataStream)

top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(DelayValueTOT)

if DataAcqusitionTOT == 1:
    #acquire_data(PulserRangeL, PulserRangeH, PulserRangeStep, top, 
    #        top.Fpga[0].Asic.SlowControl.dac_pulser, 'TOT', NofIterationsTOT, dataStream)
    acquire_data(PulserRangeL, PulserRangeH, PulserRangeStep, top, 
            top.Fpga[0].Asic.Gpio.DlyCalPulseSet, 'TOT', NofIterationsTOT, dataStream)

#######################
# Data Processing TOA #
#######################

if nTOA_TOT_Processing == 0:

    Delay = []
    HitCnt = []
    DataMean = []
    DataStdev = []

    for delay_value in range(DelayRange_low, DelayRange_high, DelayRange_step):
        # Create the File reader streaming interface
        dataReader = rogue.utilities.fileio.StreamReader()

        # Create the Event reader streaming interface
        dataStream = feb.MyFileReader()

        # Connect the file reader ---> event reader
        pr.streamConnect(dataReader, dataStream) 

        # Open the file
        dataReader.open('TestData/TOA%d.dat' %delay_value)

        # Close file once everything processed
        dataReader.closeWait()

    
        try:
            print('Processing Data for Delay = %d...' % delay_value)
        except OSError:
            pass  

        HitData = dataStream.HitData

        exec("%s = %r" % ('HitData%d' %delay_value, HitData))

        Delay.append(delay_value)

        HitCnt.append(len(HitData))
        if len(HitData) > 0:
            DataMean.append(np.mean(HitData, dtype=np.float64))
            DataStdev.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12))

        else:
            DataMean.append(0)
            DataStdev.append(0)
  
    if len(DataMean) == 0:
        raise ValueError('No hits were detected during delay sweep. Aborting!')

    # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
    index = np.where(np.sort(DataStdev))
    MeanDataStdev = np.mean(np.sort(DataStdev)[index[0][0]:len(np.sort(DataStdev))])

    # LSB estimation based on "DelayStep" value
    index=np.where(DataMean)
    fit = np.polyfit(Delay[index[0][5]:index[0][-5]], DataMean[index[0][5]:index[0][-5]], 1)
    LSBest = DelayStep/abs(fit[0])

#################################################################
# TOT Fine Interpolator Calibration

if nTOA_TOT_Processing == 1 and TOT_f_Calibration_En == 1:
    
    HitDataTOTf_cumulative = []
    HitDataTOTc_cumulative = []
    HitDataTOTf_cumulative_2to29 = []
    HitDataTOTf_cumulative0 = []
    HitDataTOTf_cumulative1 = []
    HitDataTOTf_cumulative2 = []
    HitDataTOTf_cumulative3 = []
    HitDataTOTf_cumulative4 = []
    HitDataTOTf_cumulative5 = []
    HitDataTOTf_cumulative6 = []
    HitDataTOTf_cumulative7 = []
    HitDataTOTf_cumulative8 = []
    HitDataTOTf_cumulative9 = []
    HitDataTOTf_cumulative10 = []
    HitDataTOTf_cumulative11 = []
    HitDataTOTf_cumulative12 = []
    HitDataTOTf_cumulative13 = []
    HitDataTOTf_cumulative14 = []
    HitDataTOTf_cumulative15 = []
    HitDataTOTf_cumulative16 = []
    HitDataTOTf_cumulative17 = []
    HitDataTOTf_cumulative18 = []
    HitDataTOTf_cumulative19 = []
    HitDataTOTf_cumulative20 = []
    HitDataTOTf_cumulative21 = []
    HitDataTOTf_cumulative22 = []
    HitDataTOTf_cumulative23 = []
    HitDataTOTf_cumulative24 = []
    HitDataTOTf_cumulative25 = []
    HitDataTOTf_cumulative26 = []
    HitDataTOTf_cumulative27 = []
    HitDataTOTf_cumulative28 = []
    HitDataTOTf_cumulative29 = []
    HitDataTOTf_cumulative30 = []
    HitDataTOTf_cumulative31 = []

    for i in range(PulserRangeL, PulserRangeH):
        # Create the File reader streaming interface
        dataReader = rogue.utilities.fileio.StreamReader()

        # Create the Event reader streaming interface
        dataStream = feb.MyFileReader()

        # Connect the file reader ---> event reader
        pr.streamConnect(dataReader, dataStream) 

        # Open the file
        dataReader.open('TestData/TOT%d.dat' %i)

        # Close file once everything processed
        dataReader.closeWait()

    
        try:
            print('Processing Data for Pulser = %d...' % i)
        except OSError:
            pass  

        if not nVPA_TZ:    
            HitDataTOTf = dataStream.HitDataTOTf_vpa
            HitDataTOTc = dataStream.HitDataTOTc_vpa
            HitDataTOTc_int1 = dataStream.HitDataTOTc_int1_vpa
            HitDataTOTf_cumulative = HitDataTOTf_cumulative + dataStream.HitDataTOTf_vpa
            HitDataTOTc_cumulative = HitDataTOTc_cumulative + dataStream.HitDataTOTc_vpa
        else:
            HitDataTOTf = dataStream.HitDataTOTf_tz
            HitDataTOTc = dataStream.HitDataTOTc_tz
            HitDataTOTc_int1 = dataStream.HitDataTOTc_int1_tz
            HitDataTOTf_cumulative = HitDataTOTf_cumulative + dataStream.HitDataTOTf_tz
            HitDataTOTc_cumulative = HitDataTOTc_cumulative + dataStream.HitDataTOTc_tz

        def filter_fineLin(c,i):
            if c - math.floor(c/32)*32 == i:
                return 1
            else:
                return 0

        for i_coarse in range(32):
            index = np.where(np.asarray(list(map(filter_fineLin, HitDataTOTc, np.ones(len(HitDataTOTc))*i_coarse))))
            exec("HitDataTOTf_cumulative%i = HitDataTOTf_cumulative%i + list(np.array(HitDataTOTf)[index[0]])" % (i_coarse, i_coarse))
            if i_coarse in range(2,30):
                HitDataTOTf_cumulative_2to29 = HitDataTOTf_cumulative_2to29 + list(np.array(HitDataTOTf)[index[0]])
    
    TOTf_bin_width = np.zeros(8)
    for i in range(8):
        TOTf_bin_width[i]=len(list(np.where(np.asarray(HitDataTOTf_cumulative_2to29)==i))[0])
    TOTf_bin_width = TOTf_bin_width/sum(TOTf_bin_width)

    TOTf_bin = np.zeros(10)
    for i in range(1,9):
        TOTf_bin[i]=len(list(np.where(np.asarray(HitDataTOTf_cumulative_2to29)==i-1))[0])

    index = np.where(np.sort(TOTf_bin))
    #LSB_TOTf_mean = np.mean(np.sort(TOTf_bin)[index[0][0]:len(np.sort(TOTf_bin))])/sum(TOTf_bin)
    LSB_TOTf_mean = np.mean(TOTf_bin_width[1:5])

    TOTf_bin = (TOTf_bin[1:10]/2 + np.cumsum(TOTf_bin)[0:9])/sum(TOTf_bin)
    TOTf_bin[8] = LSB_TOTf_mean

    try:
        print('TOT Fine Interpolator Bin-Widths:')
        print(TOTf_bin_width)
        print('Average TOT LSB = %f LSB_coarse' % (LSB_TOTf_mean))
    except OSError:
        pass   

    np.savetxt(TOT_f_Calibration_SAVE_file,TOTf_bin)



    TOTc_bin_width = np.zeros(32)
    for i in range(32):
        TOTc_bin_width[i]=len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i))[0]) + len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i+32))[0]) + len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i+64))[0]) + len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i+96))[0])
    TOTc_bin_width = (TOTc_bin_width/sum(TOTc_bin_width))*32

    TOTc_bin = np.zeros(34)
    for i in range(1,33):
        TOTc_bin[i]=len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i-1))[0]) + len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i-1+32))[0]) + len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i-1+64))[0]) + len(list(np.where(np.asarray(HitDataTOTc_cumulative)==i-1+96))[0])

    index = np.where(np.sort(TOTc_bin))
    LSB_TOTc_mean = np.mean(np.sort(TOTc_bin)[index[0][0]:len(np.sort(TOTc_bin))])/sum(TOTc_bin)

    TOTc_bin = (TOTc_bin[1:34]/2 + np.cumsum(TOTc_bin)[0:33])/sum(TOTc_bin)*32
    TOTc_bin[32] = LSB_TOTc_mean*32

    np.savetxt(TOT_c_Calibration_SAVE_file,TOTc_bin)


#################################################################
# Data Processing TOT

if nTOA_TOT_Processing == 1:

    DelayTOT = []
    ValidTOTCnt = []
    DataMeanTOT = []
    DataMeanTOT_coarse = []
    DataStdevTOT = []
    HitDataTOTf_cumulative = []
    
    for i in range(PulserRangeL, PulserRangeH):
        # Create the File reader streaming interface
        dataReader = rogue.utilities.fileio.StreamReader()

        # Create the Event reader streaming interface
        dataStream = feb.MyFileReader()

        # Connect the file reader ---> event reader
        pr.streamConnect(dataReader, dataStream) 

        # Open the file
        dataReader.open('TestData/TOT%d.dat' %i)

        # Close file once everything processed
        dataReader.closeWait()

    
        try:
            print('Processing Data for Pulser = %d...' % i)
        except OSError:
            pass  

        if not nVPA_TZ:    
            HitDataTOTf = dataStream.HitDataTOTf_vpa
            HitDataTOTc = dataStream.HitDataTOTc_vpa
            HitDataTOTc_int1 = dataStream.HitDataTOTc_int1_vpa
            HitDataTOTf_cumulative = HitDataTOTf_cumulative + dataStream.HitDataTOTf_vpa
        else:
            HitDataTOTf = dataStream.HitDataTOTf_tz
            HitDataTOTc = dataStream.HitDataTOTc_tz
            HitDataTOTc_int1 = dataStream.HitDataTOTc_int1_tz
            HitDataTOTf_cumulative = HitDataTOTf_cumulative + dataStream.HitDataTOTf_tz

        def filter_fineLin(c,i):
            if c - math.floor(c/32)*32 == i:
                return 1
            else:
                return 0
    
        DelayTOT.append(i)
    
        TOTf_bin = np.loadtxt(TOT_f_Calibration_LOAD_file) 
        LSB_TOTf_mean = TOTf_bin[8]
        TOTc_bin = np.loadtxt(TOT_c_Calibration_LOAD_file)
	

        def calibration_correction(f,c):
            if f == 1 and (c == 32 or c == 64):
                return 31
            else:
                return 0

        def filter_data(f,c):
            if f == 1 and c/32 == math.floor(c/32):
                return 0
            else:
                return 1

        def coarse_c(c):          
            return math.floor(c/32)*32

        def coarse_f(c):          
            return c - math.floor(c/32)*32
            
                    
        if len(HitDataTOTf) > 0:
            HitDataTOT = np.asarray(list(map(coarse_c, HitDataTOTc))) 
            HitDataTOT = HitDataTOT + np.asarray(list(map(lambda x: TOTc_bin[x], np.asarray(np.asarray(list(map(coarse_f, HitDataTOTc))), dtype=np.int))))
            HitDataTOT = HitDataTOT + 1 - np.asarray(list(map(lambda x: TOTf_bin[x], np.asarray(HitDataTOTf, dtype=np.int))))

            #HitDataTOT = list((np.asarray(HitDataTOTc) + 1 - np.asarray(HitDataTOTf)/4))

            #HitDataTOT = list(HitDataTOT + np.asarray(list(map(calibration_correction, HitDataTOTf, HitDataTOTc))))

            index = np.where(np.asarray(list(map(filter_data, HitDataTOTf, HitDataTOTc))))
            HitDataTOT = list(np.array(HitDataTOT)[(index[0])])
            #HitDataTOT = list(HitDataTOT)

        else:
            HitDataTOT = []  

        #HitDataTOT = HitDataTOTc

        exec("%s = %r" % ('HitDataTOT%d' %i, HitDataTOT))
        exec("%s = %r" % ('HitDataTOTf%d' %i, HitDataTOTf))
        exec("%s = %r" % ('HitDataTOTc%d' %i, HitDataTOTc))

        ValidTOTCnt.append(len(HitDataTOT))
        if len(HitDataTOT) > 0:        
            DataMeanTOT.append(np.mean(HitDataTOT, dtype=np.float64))
            DataMeanTOT_coarse.append(np.mean(HitDataTOTc, dtype=np.float64))
            DataStdevTOT.append(math.sqrt(math.pow(np.std(HitDataTOT, dtype=np.float64),2) + math.pow(LSB_TOTf_mean,2)/12))

        else:
            DataMeanTOT.append(0)
            DataMeanTOT_coarse.append(0)
            DataStdevTOT.append(0)

    # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
    index = np.where(np.sort(DataStdevTOT))
    MeanDataStdevTOT = np.mean(np.sort(DataStdevTOT)[index[0][0]:len(np.sort(DataStdevTOT))])

    # LSB estimation based on "DelayStep" value
    index=np.where(DataMeanTOT_coarse)
    fit = np.polyfit(DelayTOT[index[0][10]:index[0][-10]], DataMeanTOT_coarse[index[0][10]:index[0][-10]], 1)
    LSBcest = DelayStep/abs(fit[0])

#################################################################
# Print Data
if nTOA_TOT_Processing == 0:
    for delay_index, delay_value in enumerate(Delay):
        try:
            print('Delay = %d, HitCnt = %d, DataMean = %f LSB, DataStDev = %f LSB' % (delay_value, HitCnt[delay_index], DataMean[delay_index], DataStdev[delay_index]))
        except OSError:
            pass   
    try:
        print('Maximum Measured TOA = %f LSB' % np.max(DataMean))
        print('Mean Std Dev = %f LSB' % MeanDataStdev)
    except OSError:
        pass
    for delay_index, delay_value in enumerate(Delay):
        try:
            print('Delay = %d, HitCnt = %d, DataMean = %f ps, DataStDev = %f ps' % (delay_value, HitCnt[delay_index], DataMean[delay_index]*LSBest, DataStdev[delay_index]*LSBest))
        except OSError:
            pass
    try:
        print('Maximum Measured TOA = %f ps' % (np.max(DataMean)*LSBest))
        print('Mean Std Dev = %f ps' % (MeanDataStdev*LSBest))
        print('Average LSB estimate: %f ps' % LSBest)
    except OSError:
        pass
#################################################################

#################################################################
# Plot Data

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))

# LSBest = 1

if nTOA_TOT_Processing == 0:
    # Plot (0,0) ; top left
    ax1.plot(Delay, np.multiply(DataMean,LSBest))
    ax1.grid(True)
    ax1.set_title('TOA Measurment VS Programmable Delay Value', fontsize = 11)
    ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
    ax1.legend(['LSB estimate: %f ps' % LSBest],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax1.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax1.set_ylim(bottom = 0, top = np.max(np.multiply(DataMean,LSBest))+100)
else:
    # Plot (0,0) ; top left
    ax1.plot(DelayTOT, np.multiply(DataMeanTOT,LSBcest))
    #ax1.plot(DelayTOT, DataMeanTOT_coarse)
    ax1.grid(True)
    ax1.set_title('TOT Measurment VS Programmable Delay Value', fontsize = 11)
    ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
    ax1.legend(['LSB_coarse estimate: %f ps \nLSB_fine estimate: %f ps' % (LSBcest,LSB_TOTf_mean*LSBcest)],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax1.set_xlim(left = np.min(DelayTOT), right = np.max(DelayTOT))
    ax1.set_ylim(bottom = 0, top = np.max(np.multiply(DataMeanTOT,LSBcest))*1.1)
    #ax1.set_ylim(bottom = 0, top = np.max(DataMeanTOT_coarse)*1.1)

if nTOA_TOT_Processing == 0:
    # Plot (0,1) ; top right
    ax2.scatter(Delay, np.multiply(DataStdev,LSBest))
    ax2.grid(True)
    ax2.set_title('TOA Jitter VS Programmable Delay Value', fontsize = 11)
    ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax2.set_ylabel('Std. Dev. [ps]', fontsize = 10)
    ax2.legend(['Average Std. Dev. = %f ps' % (MeanDataStdev*LSBest)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax2.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax2.set_ylim(bottom = 0, top = np.max(np.multiply(DataStdev,LSBest))+20)
else:
    # Plot (0,1) ; top right
    if PlotValidCnt == 0:
        ax2.scatter(DelayTOT, np.multiply(DataStdevTOT,LSBcest))
        ax2.grid(True)
        ax2.set_title('TOT Jitter VS Programmable Delay Value', fontsize = 11)
        ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
        ax2.set_ylabel('Std. Dev. [ps]', fontsize = 10)
        ax2.legend(['Average Std. Dev. = %f ps' % MeanDataStdevTOT*LSBcest], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
        ax2.set_xlim(left = np.min(DelayTOT), right = np.max(DelayTOT))
        ax2.set_ylim(bottom = 0, top = np.max(np.multiply(DataStdevTOT,LSBcest))*1.1)
    else:
        ax2.plot(DelayTOT, ValidTOTCnt)
        ax2.grid(True)
        ax2.set_title('TOT Valid Counts VS Programmable Delay Value', fontsize = 11)
        ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
        ax2.set_ylabel('Valid Measurements', fontsize = 10)
        ax2.set_xlim(left = np.min(DelayTOT), right = np.max(DelayTOT))
        ax2.set_ylim(bottom = 0, top = np.max(ValidTOTCnt)*1.1)

if nTOA_TOT_Processing == 0:
    # Plot (1,0) ; bottom left
    exec("DataL = len(HitData%d)" % HistDelayTOA1)
    if DataL:
        #exec("ax3.hist(np.multiply(HitData%d,LSBest), bins = LSBest, align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOA1)
        hist_range = 10
        binlow = ( int(DataMean[HistDelayTOA1_index])-hist_range ) * LSBest
        binhigh = ( int(DataMean[HistDelayTOA1_index])+hist_range ) * LSBest
        hist_bin_list = np.arange(binlow, binhigh, LSBest)
        exec("ax3.hist(np.multiply(HitData%d,LSBest), bins = hist_bin_list, align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOA1)
        #exec("ax3.set_xlim(left = np.min(np.multiply(HitData%d,LSBest))-4*LSBest, right = np.max(np.multiply(HitData%d,LSBest))+4*LSBest)" % (HistDelayTOA1, HistDelayTOA1))
        ax3.set_title('TOA Measurment for Programmable Delay = %d' % HistDelayTOA1, fontsize = 11)
        ax3.set_xlabel('TOA Measurement [ps]', fontsize = 10)
        ax3.set_ylabel('N of Measrements', fontsize = 10)
        ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMean[HistDelayTOA1_index]*LSBest, DataStdev[HistDelayTOA1_index]*LSBest, HitCnt[HistDelayTOA1_index])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
else:
    # Plot (1,0)
    #exec("print(HitDataTOT%d)" % HistDelayTOT1)
    #exec("print(HitDataTOTf%d)" % HistDelayTOT1)
    #exec("print(HitDataTOTc%d)" % HistDelayTOT1)
    #exec("print(np.asarray(list(map(lambda x: TOTf_bin[x], np.asarray(HitDataTOTf%d, dtype=np.int))))*2)" % HistDelayTOT1)
    #exec("print(list(map(lambda x: x&1, np.asarray(HitDataTOTc%d))))" % HistDelayTOT1)
    if TOTf_hist == 0 and TOTc_hist == 0:
        exec("DataL = len(HitDataTOT%d)" % HistDelayTOT1)
        if DataL:
            exec("ax3.hist(HitDataTOT%d, bins = np.multiply(np.arange(512),LSB_TOTf_mean), align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOT1)
            exec("ax3.set_xlim(left = np.min(HitDataTOT%d)-10*LSB_TOTf_mean, right = np.max(HitDataTOT%d)+10*LSB_TOTf_mean)" % (HistDelayTOT1, HistDelayTOT1))
            ax3.set_title('TOT Measurment for Pulser = %d' % HistDelayTOT1, fontsize = 11)
            ax3.set_xlabel('TOT Measurement [ps]', fontsize = 10)
            ax3.set_ylabel('N of Measrements', fontsize = 10)
            ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMeanTOT[HistDelayTOT1_index]*LSBcest, DataStdevTOT[HistDelayTOT1_index]*LSBcest, ValidTOTCnt[HistDelayTOT1_index])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    else:
        if TOTf_hist == 1:
            exec("ax3.hist(HitDataTOTf%d, bins = np.arange(9), align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOT1)
            ax3.set_xlim(left = -1, right = 8)
            ax3.set_title('TOT Measurment for Pulser = %d' % HistDelayTOT1, fontsize = 11)
            ax3.set_xlabel('TOT Measurement [ps]', fontsize = 10)
            ax3.set_ylabel('N of Measrements', fontsize = 10)
            ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMeanTOT[HistDelayTOT1_index]*LSBcest, DataStdevTOT[HistDelayTOT1_index]*LSBcest, ValidTOTCnt[HistDelayTOT1_index])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
        else: 
            if TOTc_hist == 1:
                exec("ax3.hist(HitDataTOTc%d, bins = np.arange(129), align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOT1)
                ax3.set_xlim(left = -1, right = 128)
                ax3.set_title('TOT Measurment for Pulser = %d' % HistDelayTOT1, fontsize = 11)
                ax3.set_xlabel('TOT Measurement [ps]', fontsize = 10)
                ax3.set_ylabel('N of Measrements', fontsize = 10)
                ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMeanTOT[HistDelayTOT1_index]*LSBcest, DataStdevTOT[HistDelayTOT1_index]*LSBcest, ValidTOTCnt[HistDelayTOT1_index])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)

if nTOA_TOT_Processing == 0:
    # Plot (1,1)
    if PlotValidCnt == 0:
        exec("DataL = len(HitData%d)" % HistDelayTOA2)
        if DataL:
            hist_range = 10
            binlow = ( int(DataMean[HistDelayTOA2_index])-hist_range ) * LSBest
            binhigh = ( int(DataMean[HistDelayTOA2_index])+hist_range ) * LSBest
            hist_bin_list = np.arange(binlow, binhigh, LSBest)
            exec("ax4.hist(np.multiply(HitData%d,LSBest), bins = hist_bin_list, align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOA2)
            #exec("ax4.set_xlim(left = np.min(np.multiply(HitData%d,LSBest))-10*LSBest, right = np.max(np.multiply(HitData%d,LSBest))+10*LSBest)" % (HistDelayTOA2, HistDelayTOA2))
            ax4.set_title('TOA Measurment for Programmable Delay = %d' % HistDelayTOA2, fontsize = 11)
            ax4.set_xlabel('TOA Measurement [ps]', fontsize = 10)
            ax4.set_ylabel('N of Measrements', fontsize = 10)
            ax4.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMean[HistDelayTOA2_index]*LSBest, DataStdev[HistDelayTOA2_index]*LSBest, HitCnt[HistDelayTOA2_index])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    else:
        ax4.plot(Delay, HitCnt)
        ax4.grid(True)
        ax4.set_title('TOA Valid Counts VS Programmable Delay Value', fontsize = 11)
        ax4.set_xlabel('Programmable Delay Value', fontsize = 10)
        ax4.set_ylabel('Valid Measurements', fontsize = 10)
        ax4.set_xlim(left = np.min(Delay), right = np.max(Delay))
        ax4.set_ylim(bottom = 0, top = np.max(HitCnt)*1.1)
else:
    # Plot (1,1)
    if Plot_TOTf_lin == 0:
        exec("DataL = len(HitDataTOT%d)" % HistDelayTOT2)
        if DataL:
            exec("ax4.hist(HitDataTOT%d, bins = np.multiply(np.arange(512),LSB_TOTf_mean), align = 'left', edgecolor = 'k', color = 'royalblue')" % HistDelayTOT2)
            exec("ax4.set_xlim(left = np.min(HitDataTOT%d)-4*LSB_TOTf_mean, right = np.max(HitDataTOT%d)+4*LSB_TOTf_mean)" % (HistDelayTOT2, HistDelayTOT2))
            ax4.set_title('TOT Measurment for Pulser = %d' % HistDelayTOT2, fontsize = 11)
            ax4.set_xlabel('TOT Measurement [ps]', fontsize = 10)
            ax4.set_ylabel('N of Measrements', fontsize = 10)
            ax4.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMeanTOT[HistDelayTOT2_index]*LSBcest, DataStdevTOT[HistDelayTOT2_index]*LSBcest, ValidTOTCnt[HistDelayTOT2_index])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    else:
        if Plot_TOTf_lin_all == 1 and TOT_f_Calibration_En == 1:
            ax4.hist([HitDataTOTf_cumulative0,HitDataTOTf_cumulative1,HitDataTOTf_cumulative2,HitDataTOTf_cumulative3,HitDataTOTf_cumulative4,HitDataTOTf_cumulative5,HitDataTOTf_cumulative6,HitDataTOTf_cumulative7,HitDataTOTf_cumulative8,HitDataTOTf_cumulative9,HitDataTOTf_cumulative10,HitDataTOTf_cumulative11,HitDataTOTf_cumulative12,HitDataTOTf_cumulative13,HitDataTOTf_cumulative14,HitDataTOTf_cumulative15,HitDataTOTf_cumulative16,HitDataTOTf_cumulative17,HitDataTOTf_cumulative18,HitDataTOTf_cumulative19,HitDataTOTf_cumulative20,HitDataTOTf_cumulative21,HitDataTOTf_cumulative22,HitDataTOTf_cumulative23,HitDataTOTf_cumulative24,HitDataTOTf_cumulative25,HitDataTOTf_cumulative26,HitDataTOTf_cumulative27,HitDataTOTf_cumulative28,HitDataTOTf_cumulative29,HitDataTOTf_cumulative30,HitDataTOTf_cumulative31], bins = np.arange(9), label=['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31'])
            ax4.set_xlim(left = -1, right = 8)
            ax4.grid(True)
            ax4.set_title('TOT Fine Interpolation Linearity', fontsize = 11)
            ax4.set_xlabel('TOT Fine Code', fontsize = 10)
            ax4.set_ylabel('N of Measrements', fontsize = 10)    
            ax4.legend(loc='upper left', fontsize = 5)       
        else:
            ax4.hist(HitDataTOTf_cumulative, bins = np.arange(9), edgecolor = 'k', color = 'royalblue')
            ax4.set_xlim(left = -1, right = 8)
            ax4.grid(True)
            ax4.set_title('TOT Fine Interpolation Linearity', fontsize = 11)
            ax4.set_xlabel('TOT Fine Code', fontsize = 10)
            ax4.set_ylabel('N of Measrements', fontsize = 10)

plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
plt.show()
#################################################################

input("Press Enter to continue...")
top.stop()
exit()  
