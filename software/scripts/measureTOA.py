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

#DebugPrint = True
#NofIterationsTOA = 50  # <= Number of Iterations for each Delay value
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
pulseWidth = 300    # for external trigger

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
from setASICconfig import *        ##
                                                               ##
#################################################################
def acquire_data(top, useExt, DelayRange,chNb,readAllData=False): 
    pixel_stream = feb.PixelReader()
    if readAllData:
        pixel_stream.channelNumber=chNb #ALLDATA
        pixel_stream.doPrint=True #ALLDATA
    pixel_stream.checkOFtoa=args.checkOFtoa
    pixel_stream.checkOFtot=args.checkOFtot
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixel_data = []

    #pulser = top.Fpga[0].Asic.Gpio.DlyCalPulseSet #rising edge of pulser and extTrig

    for delay_value in DelayRange:
        print('Testing delay value ' + str(delay_value) )
        top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(delay_value)
        if useExt:
            top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(delay_value+pulseWidth)

        top.initialize()
        for pulse_iteration in range(args.N):#Nikola
            #print ("iter",pulse_iteration)
            top.Fpga[0].Asic.CalPulse.Start()
            time.sleep(0.001)
            if readAllData:time.sleep(0.009)#ALLDATA
            
        #print (type(pixel_stream.HitDataTOA.copy()),len(pixel_stream.HitDataTOA.copy()),pixel_stream.HitDataTOA.copy())
        pixel_data.append( pixel_stream.HitDataTOA.copy() )
        while pixel_stream.count < args.N:
            #print (pixel_stream.count,args.N)
            pass
        pixel_stream.clear()

    return pixel_data
#################################################################


def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    
    #default parameters
    pixel_number = 4
    DAC_Vth = -1
    dlyMin = 2300 
    dlyMax = 2700 
    dlyStep = 10
    outFile = 'TestData/TOAmeasurement'
    config_file = None

    
    
    # Add arguments
    parser.add_argument( "--skipExistingFile", type = argBool, required = False, default = False, help = "")
    parser.add_argument("--Rin_Vpa", type = int, required = False, default = 0, help = "RinVpa")
    parser.add_argument("--Vthc", type = int, required = False, default = -1, help = "Vth cor")
    parser.add_argument( "--ip", nargs ='+', required = False, default = ['192.168.1.10'], help = "List of IP addresses")
    parser.add_argument( "--board", type = int, required = False, default = 7,help = "Choose board")
    parser.add_argument( "--display", type = argBool, required = False, default = True, help = "show plots")
    parser.add_argument( "--debug", type = argBool, required = False, default = True, help = "debug")
    parser.add_argument( "--readAllChannels", type = argBool, required = False, default = False, help = " read all channels")
    parser.add_argument( "--useProbePA", type = argBool, required = False, default = False, help = "use probe PA")
    parser.add_argument( "--checkOFtoa", type = argBool, required = False, default = True, help = "check TOA overflow")
    parser.add_argument( "--checkOFtot", type = argBool, required = False, default = True, help = "check TOT overflow")
    parser.add_argument( "--useProbeDiscri", type = argBool, required = False, default = False, help = "use probe Discri")
    parser.add_argument("-N","--N", type = int, required = False, default = 50, help = "Nb of events")
    parser.add_argument("--Cd", type = int, required = False, default = -1, help = "Cd")
    parser.add_argument( "--useExt", type = argBool, required = False, default = False,help = "Use external trigger")
    parser.add_argument( "--cfg", type = str, required = False, default = config_file, help = "Select yml configuration file to load")  
    parser.add_argument("--ch", type = int, required = False, default = pixel_number, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = -1, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--delayMin", type = int, required = False, default = dlyMin, help = "scan start")
    parser.add_argument("--delayMax", type = int, required = False, default = dlyMax, help = "scan stop")
    parser.add_argument("--delayStep", type = int, required = False, default = dlyStep, help = "scan step")
    parser.add_argument("--out", type = str, required = False, default = outFile, help = "output file")

        # Get the arguments
    args = parser.parse_args()
    if args.useExt:
        args.Q=-1
    args.out='%sTOA_B_%d_rin_%d_ch_%d_cd_%d_Q_%d_thres_%d_vthc_%d_'%(args.out,args.board,args.Rin_Vpa,args.ch,args.Cd,args.Q,args.DAC,args.Vthc)
        

    return args
#################################################################


def measureTOA(argsip,
      board,
      useExt,
      Configuration_LOAD_file,
      pixel_number,
      Qinj,
      DAC,
      delayMin,
      delayMax,
      delayStep,
      outFile):


    if args.skipExistingFile and os.path.exists(outFile+'.txt'):
        print ('output file already exist. Skip......')
        sys.exit()
        
    #list of delay for looping
    DelayRange = range( delayMin, delayMax, delayStep )

    # choose config fileif not specified:
    if args.cfg==None:
        Configuration_LOAD_file = 'config/asic_config_B'+str(board)+'.yml'

    # Setup root class
    top = feb.Top(ip = argsip, userYaml = [Configuration_LOAD_file])

    # debug print
    if args.debug:
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

    # Set parameters for probes
    set_pixel_specific_parameters(top, pixel_number,args)

    #more parameters
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DAC)
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj)
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(delayMin)
    top.Fpga[0].Asic.CalPulse.CalPulseWidth.set(0x12)#was 0x2

    
    # Data Acquisition for TOA
    #with external
    if useExt:
        print("Will use external trigger")
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x0)


    
    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()

    pixel_data = acquire_data(top, useExt, DelayRange,args.ch,readAllData=args.readAllChannels)
    
    #######################
    # Data Processing TOA #
    #######################
    
    num_valid_TOA_reads = len(pixel_data)
    if len(pixel_data) == 0: raise ValueError('No hits were detected during delay sweep. Aborting!')

    HitCnt = []
    DataMean = np.zeros(num_valid_TOA_reads)
    DataStdev = np.zeros(num_valid_TOA_reads)
    allTOAdata = []
    


    
    for delay_index, delay_value in enumerate(DelayRange):
        okTOA=np.array(pixel_data[delay_index])!=127 #used to remove saturated toa
        #print(okTOA)
        HitDataTOA = np.array(pixel_data[delay_index])[okTOA]
        HitCnt.append(len(HitDataTOA))
        allTOAdata.append(HitDataTOA)
        if len(HitDataTOA) > 0.5*args.N:
            DataMean[delay_index] = np.mean(HitDataTOA, dtype=np.float64)
            DataStdev[delay_index] = math.sqrt(math.pow(np.std(HitDataTOA, dtype=np.float64),2)+1/12)
        #print (delay_value,HitDataTOA,DataStdev[delay_index])
    
    # The following calculations ignore points with no data (i.e. Std.Dev = 0)
    nonzero = DataMean != 0
    
    # Average Std. Dev. Calculation; Points with no data (i.e. Std.Dev.= 0) are ignored
    MeanDataStdev = np.mean(DataStdev[nonzero])
    
    # LSB estimation based on "DelayStep" value, again ignoring zero values
    safety_bound = 0
    if len(DelayRange)>10:
        safety_bound = 2 #so we don't measure too close to the edges of the pulse        
    Delay = np.array(DelayRange)
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
    #for delay_index, delay_value in enumerate(DelayRange):
    #    print('Delay = %d, HitCnt = %d, DataMean = %f LSB, DataStDev = %f LSB / %f ps' % (delay_value, HitCnt[delay_index], DataMean[delay_index], DataStdev[delay_index], DataStdev[delay_index]*LSBest))
    print('Maximum Measured TOA = %f LSB / %f ps' % ( np.max(DataMean), (np.max(DataMean)*LSBest) ) )
    print('Mean Std Dev = %f LSB / %f ps' % ( MeanDataStdev, (MeanDataStdev*LSBest) ) )
    print('Average LSB estimate: %f ps' % LSBest)
    #################################################################
    #################################################################
    # Save Data
    #################################################################


    
    if os.path.exists(outFile+'.txt'):
      ts = str(int(time.time()))
      outFile = outFile+"_"+ts
    outFile = outFile+'.txt'
    
    ff = open(outFile,'a')
    ff.write('TOA measurement vs Delay ---- '+time.ctime()+'\n')
    if useExt:
        ff.write('Using ext trigger, width = '+str(pulseWidth)+'\n')
    ff.write('Pixel = '+str(pixel_number)+'\n')
    ff.write('config file = '+Configuration_LOAD_file+'\n')
    ff.write('NofIterations = '+str(args.N)+'\n')
    #ff.write('cmd_pulser = '+str(Qinj)+'\n')
    #ff.write('Delay DAC = '+str(DelayValue)+'\n')
    ff.write('LSBest = '+str(LSBest)+'\n')
    #ff.write('Threshold = '+str(DACvalue)+'\n')
    #ff.write('N hits = '+str(sum(HitCnt))+'\n')
    #ff.write('Number of events = '+str(len(HitDataTOA))+'\n')
    ff.write('mean value = '+str(DataMean)+'\n')
    ff.write('sigma = '+str(DataStdev)+'\n')
    ff.write('Pulse delay   TOA '+'\n')
    allTOA = []
    allDelay = []
    for idel in range(len(DelayRange)):
      pulser = DelayRange[idel]
      for itoa in range(len(allTOAdata[idel])):
        ff.write(str(pulser)+' '+str(allTOAdata[idel][itoa])+'\n')
        allTOA.append(allTOAdata[idel][itoa])
        allDelay.append(pulser)
    ff.close()
    
    print('Saved file '+outFile)


    print ("-------------------------------------------------------")
    print("The arguments was:")
    print(args)
    print("Config file was:", Configuration_LOAD_file)
    printStatus(top)
    print ("-------------------------------------------------------")

    

    #################################################################
    # Plot Data
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))

    # Plot (0,0) ; top left
    #ax1.plot(Delay, np.multiply(DataMean,LSBest))

    xedges = range(delayMin,delayMax)#DelayRange#np.array(range(0,65))-0.5
    yedges = range(0,128,2)
    HTOA, xedges, yedges = np.histogram2d(allDelay, allTOA, bins=(xedges, yedges))
    HTOA = HTOA.T  # Let each row list bins with common y range.
    X, Y = np.meshgrid(xedges, yedges)        
    ax1.pcolormesh(X, Y, HTOA,cmap=plt.cm.YlOrRd)
    ax1.scatter(Delay, DataMean, facecolors='none', edgecolors='b')
    #ax1.plot(Delay, DataMean)
    #ax1.grid(True)
    ax1.set_title('TOA Measurment VS Programmable Delay Value', fontsize = 11)
    ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
    ax1.legend(['LSB estimate: %f ps' % LSBest],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    #ax1.set_ylim(bottom = 0, top = np.max(np.multiply(DataMean,LSBest))+100)
    ax1.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax1.set_ylim(bottom = 0, top = 128)


    LSBForPlot=20
    if LSBest<50:
        LSBForPlot=LSBest
    # Plot (0,1) ; top right
    #ax2.scatter(Delay, np.multiply(DataStdev,LSBForPlotest))
    ax2.scatter(Delay, np.multiply(DataStdev,LSBForPlot))
    ax2.grid(True)
    ax2.set_title('TOA Jitter VS Programmable Delay Value', fontsize = 11)
    ax2.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax2.set_ylabel('Std. Dev. [ps] (LSBForPlot='+str(round(LSBForPlot))+'ps)', fontsize = 10)
    ax2.legend(['Average Std. Dev. = %f ps' % (MeanDataStdev*LSBForPlot)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax2.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax2.set_ylim(bottom = 0, top = np.max(np.multiply(DataStdev,LSBForPlot))+20)
    ax2.set_ylim(bottom = 0, top = 100)

    # Plot (1,0) ; bottom left

    delay_index_to_plot = int(len(DelayRange)/2)
    # for delay_index, delay_value in enumerate(DelayRange): #find a good delay value to plot
    #     #I'd say having 80% of hits come back is good enough to plot
    #     if HitCnt[delay_index] > args.N * 0.8:
    #         delay_index_to_plot = delay_index+10
    #         break

    if delay_index_to_plot != -1:
        hist_range = 10
        LSB=LSBest
        binlow = ( int(DataMean[delay_index_to_plot])-hist_range ) * LSB
        binhigh = ( int(DataMean[delay_index_to_plot])+hist_range ) * LSB
        hist_bin_list = np.arange(binlow, binhigh, LSB)
        ax3.hist(np.multiply(pixel_data[delay_index_to_plot],LSB), bins = hist_bin_list, align = 'left', edgecolor = 'k', color = 'royalblue')
        ax3.set_title('TOA Measurment for Programmable Delay = %d' % DelayRange[delay_index_to_plot], fontsize = 11)
        ax3.set_xlabel('TOA Measurement [ps]', fontsize = 10)
        ax3.set_ylabel('N of Measrements', fontsize = 10)
        ax3.legend(['Mean = %f ps \nStd. Dev. = %f ps \nN of Events = %d' % (DataMean[delay_index_to_plot]*LSB, DataStdev[delay_index_to_plot]*LSB, HitCnt[delay_index_to_plot])], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)

    # Plot (1,1)
    ax4.plot(Delay, HitCnt)
    ax4.grid(True)
    ax4.set_title('TOA Valid Counts VS Programmable Delay Value', fontsize = 11)
    ax4.set_xlabel('Programmable Delay Value', fontsize = 10)
    ax4.set_ylabel('Valid Measurements', fontsize = 10)
    ax4.set_xlim(left = np.min(Delay), right = np.max(Delay))
    ax4.set_ylim(bottom = 0, top = np.max(HitCnt)*1.1)
    plt.subplots_adjust(hspace = 0.35, wspace = 0.2)

        
    plt.savefig(outFile.replace(".txt",".pdf"))
    if args.display:plt.show()
    #################################################################
    
    time.sleep(0.5)
    # Close
    top.stop()
    #################################################################




if __name__ == "__main__":
    args = parse_arguments()
    print(args)

    measureTOA(args.ip, args.board, args.useExt,args.cfg, args.ch, args.Q, args.DAC, args.delayMin, args.delayMax, args.delayStep, args.out)
