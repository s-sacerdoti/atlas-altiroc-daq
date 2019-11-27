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
asicVersion = 1
DebugPrint = True
NofIterations = 16  # <= Number of Iterations for each Delay value
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
#pulseWidth = 500
riseEdge = 2450
fallEdge = 2500
#LSB_TOTc = 160
#LSB_TOA = 20
LSB_TOTc = 1 #not using LSB values for now
LSB_TOA = 1
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
def acquire_data(top, useExt, pulserRange): 
    pixel_stream = feb.PixelReader()
    pixel_stream.checkOFtoa=False
    pixel_stream.checkOFtot=True
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixel_data = {
        'HitDataTOA' : [],
        'HitDataTOT': [],
        'HitDataTOTf': [],
        'HitDataTOTc': [],
        'HitDataTOTc_int1': [],
        'TOAOvflow' : [],
        'TOTOvflow' : [],
        'SeqCnt'    : [],
        'TrigCnt'   : [],
        'TimeStamp' : []
    }

    pulser = top.Fpga[0].Asic.SlowControl.dac_pulser
    for pulse_value in pulserRange:
        print('Scanning Pulse value of ' + str(pulse_value))
        pulser.set(pulse_value)

        for pulse_iteration in range(NofIterations):
            if (asicVersion == 1): 
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.001)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)
    #pulser = top.Fpga[0].Asic.Gpio.DlyCalPulseSet #rising edge of pulser and extTrig

    #for delay_value in pulseRange:
    #    print('Testing delay value ' + str(delay_value) )
    #    pulser.set(delay_value)
    #    #trying to follow what the DevGui Start button does...
    #    top.Fpga[0].Asic.Trig.countReset()
    #    top.Fpga[0].Asic.Readout.SeqCntRst()
    #    if useExt:
    #        #set the falling edge of the ext trigger
    #        top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(delay_value+pulseWidth)

    #    for pulse_iteration in range(NofIterations):
    #        #top.Fpga[0].Asic.CalPulse.Start()
    #        top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
    #        time.sleep(0.001)

        pixel_data['HitDataTOA'].append( pixel_stream.HitDataTOA.copy() )
        pixel_data['HitDataTOT'].append( pixel_stream.HitDataTOT.copy() )
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
    outFile = 'TestData/TWmeasurement'
    config_file = 'config/asic_config_B8.yml' # <= Path to the Configuration File to be Loaded
    ipIN=['192.168.1.10']
    
    
    # Add arguments
    parser.add_argument( "--ip", nargs ='+', required = False, default = ipIN, help = "List of IP addresses")
    parser.add_argument( "--useProbe", type = argBool, required = False, default = False, help = "use probe")
    parser.add_argument( "--board", type = int, required = False, default = 7, help = "Choose board")  
    parser.add_argument( "--cfg", required = False, default = config_file, help = "Select yml configuration file to load")  
    parser.add_argument( "--useExt", type = argBool, required = False, default = False,help = "Use external trigger")
    parser.add_argument("--ch", type = int, required = False, default = pixel_number, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = Qinj, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--pulserMin", type = int, required = False, default = minPulser, help = "scan start")
    parser.add_argument("--pulserMax", type = int, required = False, default = maxPulser, help = "scan stop")
    parser.add_argument("--pulserStep", type = int, required = False, default = pulsStep, help = "scan step")
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
      pulserMin,
      pulserMax,
      pulserStep,
      outFile):

    pulseRange = range( pulserMin, pulserMax, pulserStep )

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
    if not args.useProbe:
        top.Fpga[0].Asic.Probe.en_probe_pa.set(0) # was bitset
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0) # was bitset
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x0)
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x0)#change the results!!!!
    
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DAC)
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj)

    # Data Acquisition for TOA
    #with external
    if useExt:
        print("Will use external trigger")
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x0)
    else:
        top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(riseEdge)
        top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)

    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()

    #getting TOA and TOT not in overflow
    pixel_data = acquire_data(top, useExt, pulseRange)
    
    #######################
    # Data Processing #
    #######################
    
    if len(pixel_data) == 0: raise ValueError('No hits were detected during delay sweep. Aborting!')
    
    ValidTOACnt = np.zeros( len(pulseRange) )
    ValidTOTCnt = np.zeros( len(pulseRange) )
    TOAmean = np.zeros( len(pulseRange) )
    TOTmean = np.zeros( len(pulseRange) )
    TOAjit = np.zeros( len(pulseRange) )
    TOTjit = np.zeros( len(pulseRange) )
    allTOAdata = []
    allTOTdata = []
    
    for delay_index, delay_value in enumerate(pulseRange):
        HitDataTOA = pixel_data['HitDataTOA'][delay_index]
        HitDataTOTc = np.asarray( pixel_data['HitDataTOTc'][delay_index])
        HitDataTOTf = np.asarray( pixel_data['HitDataTOTf'][delay_index])
        HitDataTOT = list( (1 + HitDataTOTc - HitDataTOTf/4) * LSB_TOTc )
        #HitCnt.append(len(HitDataTOA)) #all data should have equal length
        ValidTOACnt[delay_index] = len(HitDataTOA)
        ValidTOTCnt[delay_index] = len(HitDataTOT)
        allTOAdata.append(HitDataTOA)
        allTOTdata.append(HitDataTOT)
        if len(HitDataTOA) > 0:
            TOAmean[delay_index] = np.mean(HitDataTOA, dtype=np.float64)
            TOAjit[delay_index] = math.sqrt(math.pow(np.std(HitDataTOA, dtype=np.float64),2)+1/12)
            TOTmean[delay_index] = np.mean(HitDataTOT, dtype=np.float64)
            TOTjit[delay_index] = math.sqrt(math.pow(np.std(HitDataTOT, dtype=np.float64),2)+1/12)
    
    # The following calculations ignore points with no data (i.e. Std.Dev = 0)
    nonzeroTOA = TOAmean != 0
    nonzeroTOT = TOAmean != 0
    
    # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
    print(TOAjit)
    print(nonzeroTOA)
    MeanTOAjit = np.mean(TOAjit[nonzeroTOA])
    MeanTOTjit = np.mean(TOTjit[nonzeroTOT])
    
    #################################################################
    # Print Data
    for delay_index, delay_value in enumerate(pulseRange):
        print('Delay = %d, ValidTOACnt = %d, TOAmean = %f LSB, DataStDev = %f LSB / %f ps' % (delay_value, ValidTOACnt[delay_index], TOAmean[delay_index], TOAjit[delay_index], TOAjit[delay_index]))
    print('Maximum Measured TOA = %f LSB / %f ps' % ( np.max(TOAmean), (np.max(TOAmean)*LSB_TOA) ) )
    print('Mean Std Dev = %f LSB / %f ps' % ( MeanTOAjit, (MeanTOAjit*LSB_TOA) ) )
    print('Average LSB estimate: %f ps' % LSB_TOA)
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
#    if useExt:
#        ff.write('Using ext trigger, width = '+str(pulseWidth)+'\n')
    ff.write('Pixel = '+str(pixel_number)+'\n')
    ff.write('config file = '+Configuration_LOAD_file+'\n')
    ff.write('NofIterations = '+str(NofIterations)+'\n')
    #ff.write('cmd_pulser = '+str(Qinj)+'\n')
    #ff.write('Delay DAC = '+str(DelayValue)+'\n')
    ff.write('LSB_TOA = '+str(LSB_TOA)+'\n')
    #ff.write('Threshold = '+str(DACvalue)+'\n')
    #ff.write('N hits = '+str(sum(ValidTOACnt))+'\n')
    #ff.write('Number of events = '+str(len(HitData))+'\n')
    ff.write('mean value = '+str(TOAmean)+'\n')
    ff.write('sigma = '+str(TOAjit)+'\n')
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
    #ax1.plot(Delay, np.multiply(TOAmean,LSB_TOA))
    ax1.plot(pulseRange, TOAmean)
    ax1.grid(True)
    ax1.set_title('TOA Measurment VS Programmable Delay Value', fontsize = 11)
    ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
    ax1.legend(['LSB estimate: %f ps' % LSB_TOA],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    #ax1.set_ylim(bottom = 0, top = np.max(np.multiply(TOAmean,LSB_TOA))+100)
    ax1.set_xlim(left = np.min(pulseRange), right = np.max(pulseRange))
    ax1.set_ylim(bottom = 0, top = np.max(TOAmean)+10)
    
    # Plot (0,1) ; top right
    ax2.scatter(pulseRange, np.multiply(TOAjit,LSB_TOA))
    ax2.grid(True)
    ax2.set_title('TOA Jitter VS Programmable Delay Value', fontsize = 11)
    ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax2.set_ylabel('Std. Dev. [ps]', fontsize = 10)
    ax2.legend(['Average Std. Dev. = %f ps' % (MeanTOAjit*LSB_TOA)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax2.set_xlim(left = np.min(pulseRange), right = np.max(pulseRange))
    ax2.set_ylim(bottom = 0, top = np.max(np.multiply(TOAjit,LSB_TOA))+20)
    
    # Plot (1,0) ; bottom left
    
    #delay_index_to_plot = -1
    #for delay_index, delay_value in enumerate(pulseRange): #find a good delay value to plot
    #    #I'd say having 80% of hits come back is good enough to plot
    #    if ValidTOACnt[delay_index] > NofIterations * 0.8:
    #        delay_index_to_plot = delay_index
    #        break
    #
    #if delay_index_to_plot != -1:
    #    hist_range = 10
    #    binlow = ( int(TOAmean[delay_index_to_plot])-hist_range ) * LSB_TOA
    #    binhigh = ( int(TOAmean[delay_index_to_plot])+hist_range ) * LSB_TOA
    #    hist_bin_list = np.arange(binlow, binhigh, LSB_TOA)
    #    ax3.hist(np.multiply(pixel_data[delay_index_to_plot],LSB_TOA), bins = hist_bin_list, align = 'left', edgecolor = 'k', color = 'royalblue')
    #    ax3.set_title('TOA Measurment for Programmable Delay = %d' % pulseRange[delay_index_to_plot], fontsize = 11)
    #    ax3.set_xlabel('TOA Measurement [ps]', fontsize = 10)
    #    ax3.set_ylabel('N of Measrements', fontsize = 10)
    #    ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (TOAmean[delay_index_to_plot]*LSB_TOA, TOAjit[delay_index_to_plot]*LSB_TOA, ValidTOACnt[delay_index_to_plot])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax3.plot(TOAmean,TOTmean)
    ax3.grid(True)
    ax3.set_title('TOA mean vs TOT mean', fontsize = 11)
    #ax3.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    #ax3.set_ylabel('Mean Value [ps]', fontsize = 10)
    #ax3.legend(['LSB estimate: %f ps' % LSB_TOA],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    #ax1.set_ylim(bottom = 0, top = np.max(np.multiply(TOAmean,LSB_TOA))+100)
    #ax3.set_xlim(left = np.min(pulseRange), right = np.max(pulseRange))
    #ax3.set_ylim(bottom = 0, top = np.max(TOAmean)+10)

    # Plot (1,1)
    ax4.plot(pulseRange, ValidTOACnt)
    ax4.grid(True)
    ax4.set_title('TOA Valid Counts VS Programmable Delay Value', fontsize = 11)
    ax4.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax4.set_ylabel('Valid Measurements', fontsize = 10)
    ax4.set_xlim(left = np.min(pulseRange), right = np.max(pulseRange))
    ax4.set_ylim(bottom = 0, top = np.max(ValidTOACnt)*1.1)
    
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
    measureTW(args.ip, args.board, args.useExt,args.cfg, args.ch, args.Q, args.DAC, args.pulserMin, args.pulserMax, args.pulserStep, args.out)
