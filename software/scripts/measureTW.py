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
NofIterations = 16  # <= Number of Iterations for each Delay value
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
pulseWidth = 500
riseEdge = 2400
fallEdge = 3000
LSB_TOTc = 160
LSB_TOA = 20
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
def acquire_data(top, useExt, pulseRange): 
    pixel_stream = feb.PixelReader()    
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixel_data = {
        'allTOAdata' : [],
        'HitDataTOA' : [],
        'allTOTdata' : [],
        'HitDataTOTf': [],
        'HitDataTOTc': [],
        'HitDataTOTc_int1': [],
        'TOAOvflow' : [],
        'TOTOvflow' : [],
        'SeqCnt'    : [],
        'TrigCnt'   : [],
        'TimeStamp' : []
    }
    pulser = top.Fpga[0].Asic.Gpio.DlyCalPulseSet #rising edge of pulser and extTrig

    for delay_value in pulseRange:
        print('Testing delay value ' + str(delay_value) )
        pulser.set(delay_value)
        if useExt:
            #set the falling edge of the ext trigger
            top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(delay_value+pulseWidth)

        for pulse_iteration in range(NofIterations):
            top.Fpga[0].Asic.CalPulse.Start()
            time.sleep(0.001)
        pixel_data['allTOAdata'].append( pixel_stream.HitDataTOT.copy() )
        pixel_data['HitDataTOA'].append( pixel_stream.HitDataTOA.copy() )
        pixel_data['allTOTdata'].append( pixel_stream.HitDataTOT.copy() )
        pixel_data['HitDataTOTf'].append( pixel_stream.HitDataTOTf_vpa.copy() )
        pixel_data['HitDataTOTc'].append( pixel_stream.HitDataTOTc_vpa.copy() )
        pixel_data['HitDataTOTc_int1'].append( pixel_stream.HitDataTOTc_int1_vpa.copy() )
        pixel_data['TOAOvflow'].append( pixel_stream.TOAOvflow.copy() )
        pixel_data['TOTOvflow'].append( pixel_stream.TOTOvflow.copy() )
        pixel_data['SeqCnt'   ].append( pixel_stream.SeqCnt.copy() )
        pixel_data['TrigCnt'  ].append( pixel_stream.TrigCnt.copy() )
        pixel_data['TimeStamp'].append( pixel_stream.TimeStamp.copy() )

        while pixel_stream.count < NofIterations: pass
        pixel_stream.clear()
    return pixel_data
#################################################################
def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    
    #default parameters
    pixel_number = 4
    DAC_Vth = 320
    Qinj = 13 #10fc
    minPulser = 2300 
    maxPulser = 2700 
    pulsStep = 10
    outFile = 'TestData/TOAmeasurement'
    config_file = 'config/asic_config_B8.yml' # <= Path to the Configuration File to be Loaded
    ipIN=['192.168.1.10']
    
    
    # Add arguments
    parser.add_argument( "--ip", nargs ='+', required = False, default = ipIN, help = "List of IP addresses")  
    parser.add_argument( "--board", type = int, required = False, default = 7, help = "Choose board")  
    parser.add_argument( "--cfg", required = False, default = config_file, help = "Select yml configuration file to load")  
    parser.add_argument( "--useExt", type = bool, required = False, default = False,help = "Use external trigger")
    parser.add_argument("--ch", type = int, required = False, default = pixel_number, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = Qinj, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--pulseMin", type = int, required = False, default = minPulser, help = "scan start")
    parser.add_argument("--pulseMax", type = int, required = False, default = maxPulser, help = "scan stop")
    parser.add_argument("--pulseStep", type = int, required = False, default = pulsStep, help = "scan step")
    parser.add_argument("--out", type = str, required = False, default = outFile, help = "output file")

    # Get the arguments
    args = parser.parse_args()
    return args
#################################################################


def measureTW(argsip,
      board,
      useExt,
      Configuration_LOAD_file,
      pixel_number,
      Qinj,
      DAC,
      pulseMin,
      pulseMax,
      pulseStep,
      outFile):

    pulseRange = range( pulseMin, pulseMax, pulseStep )

    #choose config file:
    Configuration_LOAD_file = 'config/asic_config_B7.yml'
    if board == 8:
        Configuration_LOAD_file = 'config/asic_config_B8.yml'
    elif board == 3:
        Configuration_LOAD_file = 'config/asic_config_B3.yml'
    elif board == 2:
        Configuration_LOAD_file = 'config/asic_config_B2.yml'

    # Setup root class
    top = feb.Top(ip = argsip, userYaml = [Configuration_LOAD_file])
    
    if DebugPrint:
        top.Fpga[0].AxiVersion.printStatus()
        # Tap the streaming data interface (same interface that writes to file)
        dataStream = feb.PrintEventReader()    
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

    #testing resets
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)

    set_pixel_specific_parameters(top, pixel_number)
    
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DAC)
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj)

    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()

    # Data Acquisition for TOA
    #with external
    if useExt:
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x0)

    #getting TOA and TOT not in overflow
    pixel_data = acquire_data(top, useExt, pulseRange)
    
    #######################
    # Data Processing #
    #######################
    
    num_events = len(pixel_data['HitDataTOA']) #all should have same length
    if len(pixel_data) == 0: raise ValueError('No hits were detected during delay sweep. Aborting!')
    
    ValidTOACnt = []
    ValidTOTCnt = []
    TOAmean = []
    TOTmean = []
    TOAjit = []
    TOTjit = []
    allTOAdata = []
    allTOTdata = []
    
    for delay_index, delay_value in enumerate(pulseRange):
        HitDataTOA = pixel_data['HitDataTOA'][delay_index]
        HitDataTOT = pixel_data['HitDataTOT'][delay_index]
        HitCnt.append(len(HitData))
        allTOAdata.append(HitData)
        if len(HitData) > 0:
            DataMean[delay_index] = np.mean(HitData, dtype=np.float64)
            DataStdev[delay_index] = math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12)
    
    # The following calculations ignore points with no data (i.e. Std.Dev = 0)
    nonzero = DataMean != 0
    
    # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
    MeanDataStdev = np.mean(DataStdev[nonzero])
    
    # LSB estimation based on "DelayStep" value, again ignoring zero values
    safety_bound = 2 #so we don't measure too close to the edges of the pulse 
    Delay = np.array(pulseRange)
    fit_x_values = Delay[nonzero][safety_bound:-safety_bound]
    fit_y_values = DataMean[nonzero][safety_bound:-safety_bound]
    if len(fit_x_values) == 0: 
        LSBest = 99999
        print('\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('WARNING! YOU HAVE TRIED TO FIT OVER TOO FEW VALUES!')
        print('LSB ESTIMATE CALCULATION IS BEING SKIPPED!')
        print('LSB ESTIMATE DEFAULTED TO ' + str(LSBest) )
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n')
    else:
        linear_fit_slope = np.polyfit(fit_x_values, fit_y_values, 1)[0]
        LSBest = DelayStep/abs(linear_fit_slope)
    
    
    #################################################################
    # Print Data
    for delay_index, delay_value in enumerate(pulseRange):
        print('Delay = %d, HitCnt = %d, DataMean = %f LSB, DataStDev = %f LSB / %f ps' % (delay_value, HitCnt[delay_index], DataMean[delay_index], DataStdev[delay_index], DataStdev[delay_index]*LSBest))
    print('Maximum Measured TOA = %f LSB / %f ps' % ( np.max(DataMean), (np.max(DataMean)*LSBest) ) )
    print('Mean Std Dev = %f LSB / %f ps' % ( MeanDataStdev, (MeanDataStdev*LSBest) ) )
    print('Average LSB estimate: %f ps' % LSBest)
    #################################################################
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
    ff.write('NofIterations = '+str(NofIterations)+'\n')
    #ff.write('cmd_pulser = '+str(Qinj)+'\n')
    #ff.write('Delay DAC = '+str(DelayValue)+'\n')
    ff.write('LSBest = '+str(LSBest)+'\n')
    #ff.write('Threshold = '+str(DACvalue)+'\n')
    #ff.write('N hits = '+str(sum(HitCnt))+'\n')
    #ff.write('Number of events = '+str(len(HitData))+'\n')
    ff.write('mean value = '+str(DataMean)+'\n')
    ff.write('sigma = '+str(DataStdev)+'\n')
    ff.write('Pulse delay   TOA '+'\n')
    for idel in range(len(pulseRange)):
      pulser = pulseRange[idel]
      for itoa in range(len(allTOAdata[idel])):
        ff.write(str(pulser)+' '+str(allTOAdata[idel][itoa])+'\n')
    #ff.write('TOAvalues = '+str(HitDataTOT)+'\n')
    ff.close()
    
    print('Saved file '+outFile)
 
    #################################################################
    # Plot Data
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))
    
    # Plot (0,0) ; top left
    #ax1.plot(Delay, np.multiply(DataMean,LSBest))
    ax1.plot(Delay, DataMean)
    ax1.grid(True)
    ax1.set_title('TOA Measurment VS Programmable Delay Value', fontsize = 11)
    ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
    ax1.legend(['LSB estimate: %f ps' % LSBest],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    #ax1.set_ylim(bottom = 0, top = np.max(np.multiply(DataMean,LSBest))+100)
    ax1.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax1.set_ylim(bottom = 0, top = np.max(DataMean)+10)
    
    # Plot (0,1) ; top right
    ax2.scatter(Delay, np.multiply(DataStdev,LSBest))
    ax2.grid(True)
    ax2.set_title('TOA Jitter VS Programmable Delay Value', fontsize = 11)
    ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax2.set_ylabel('Std. Dev. [ps]', fontsize = 10)
    ax2.legend(['Average Std. Dev. = %f ps' % (MeanDataStdev*LSBest)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax2.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax2.set_ylim(bottom = 0, top = np.max(np.multiply(DataStdev,LSBest))+20)
    
    # Plot (1,0) ; bottom left
    
    delay_index_to_plot = -1
    for delay_index, delay_value in enumerate(pulseRange): #find a good delay value to plot
        #I'd say having 80% of hits come back is good enough to plot
        if HitCnt[delay_index] > NofIterations * 0.8:
            delay_index_to_plot = delay_index
            break
    
    if delay_index_to_plot != -1:
        hist_range = 10
        binlow = ( int(DataMean[delay_index_to_plot])-hist_range ) * LSBest
        binhigh = ( int(DataMean[delay_index_to_plot])+hist_range ) * LSBest
        hist_bin_list = np.arange(binlow, binhigh, LSBest)
        ax3.hist(np.multiply(pixel_data[delay_index_to_plot],LSBest), bins = hist_bin_list, align = 'left', edgecolor = 'k', color = 'royalblue')
        ax3.set_title('TOA Measurment for Programmable Delay = %d' % pulseRange[delay_index_to_plot], fontsize = 11)
        ax3.set_xlabel('TOA Measurement [ps]', fontsize = 10)
        ax3.set_ylabel('N of Measrements', fontsize = 10)
        ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMean[delay_index_to_plot]*LSBest, DataStdev[delay_index_to_plot]*LSBest, HitCnt[delay_index_to_plot])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    
    # Plot (1,1)
    ax4.plot(Delay, HitCnt)
    ax4.grid(True)
    ax4.set_title('TOA Valid Counts VS Programmable Delay Value', fontsize = 11)
    ax4.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax4.set_ylabel('Valid Measurements', fontsize = 10)
    ax4.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax4.set_ylim(bottom = 0, top = np.max(HitCnt)*1.1)
    
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

    measureTW(args.ip, args.board, args.useExt,args.cfg, args.ch, args.Q, args.DAC, args.pulseMin, args.pulseMax, args.pulseStep, args.out)
