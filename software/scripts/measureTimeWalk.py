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
DelayStep = 9.5582  # <= Estimate of the Programmable Delay Step in ps (measured on 10JULY2019)
pulseWidth = 300

#################################################################
                                                               ##
import sys                                                     ##
import rogue                                                   ##
import time                                                    ##
import random                                                  ##
import argparse                                                ##
import pickle                                                  ##
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
def acquire_data(top, useExt,QRange): 
    pixel_stream = feb.PixelReader()    
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA

    pixel_data = {
        'HitDataTOA': [],
        'HitDataTOTf': [],
        'HitDataTOTc': [],
        #'HitDataTOT': [],
        #'allTOTdata' : [],
        #'HitDataTOTc_int1': []
    }

     #rising edge of pulser and extTrig


    for Q_value in QRange:
        print('Testing Q value ' + str(Q_value) )
        top.Fpga[0].Asic.SlowControl.dac_pulser.set(Q_value)
        top.initialize()#You MUST call this function after doing ASIC configurations!!!
        if useExt:
            top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(delay_value+pulseWidth)


        for pulse_iteration in range(args.N):
            top.Fpga[0].Asic.CalPulse.Start()
            time.sleep(0.001)
        pixel_data['HitDataTOA'].append( pixel_stream.HitDataTOA.copy() )
        #pixel_data['allTOTdata'].append( pixel_stream.HitDataTOT.copy() )
        pixel_data['HitDataTOTf'].append( pixel_stream.HitDataTOTf_vpa.copy() )
        pixel_data['HitDataTOTc'].append( pixel_stream.HitDataTOTc_vpa.copy() )
        #pixel_data['HitDataTOTc_int1'].append( pixel_stream.HitDataTOTc_int1_vpa.copy() )
        while pixel_stream.count < args.N: pass
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
    dly = 2450 
    outFile = 'TestData/TimeWalk'

    # Add arguments
    parser.add_argument( "--ip", nargs ='+', required = False, default = ['192.168.1.10'], help = "List of IP addresses")
    parser.add_argument( "--board", type = int, required = False, default = 7,help = "Choose board")
    parser.add_argument( "--useProbePA", type = argBool, required = False, default = False, help = "use probe PA")
    parser.add_argument( "--useProbeDiscri", type = argBool, required = False, default = False, help = "use probe Discri")
    parser.add_argument( "--useExt", type = argBool, required = False, default = False,help = "Use external trigger")
    parser.add_argument( "--cfg", type = str, required = False, default = None, help = "Select yml configuration file to load")  
    parser.add_argument("--ch", type = int, required = False, default = pixel_number, help = "channel")
    parser.add_argument("-N", type = int, required = False, default = 50, help = "Nb of events")

    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--delay", type = int, required = False, default = dly, help = "scan start")
    parser.add_argument("--QMin", type = int, required = False, default = 13, help = "scan start")
    parser.add_argument("--QMax", type = int, required = False, default = 14, help = "scan start")
    parser.add_argument("--QStep", type = int, required = False, default = 1, help = "scan start")
    parser.add_argument("--Qconv", type = float, required = False, default = 1, help = "scan start")
    parser.add_argument("--LSBTOA", type = float, required = False, default = 20, help = "LSB TOA")
    parser.add_argument("--LSBTOTc", type = float, required = False, default = 160, help = "LSB TOTc")
    parser.add_argument("--LSBTOTf", type = float, required = False, default = 40, help = "LSB TOTf")
    parser.add_argument("--out", type = str, required = False, default = outFile, help = "output file")

    # Get the arguments
    args = parser.parse_args()
    return args
#################################################################


def measureTimeWalk(argsip,
      board,
      useExt,
      Configuration_LOAD_file,
      pixel_number,
      QMin,
      QMax,
      QStep,
      DAC,
      delay,
      outFile):

    QRange = range( QMin, QMax, QStep )


    #choose config fileif not specified:
    if args.cfg==None:
        Configuration_LOAD_file = 'config/asic_config_B'+str(board)+'.yml'
        
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
    if not args.useProbePA:
        top.Fpga[0].Asic.Probe.en_probe_pa.set(0) # was bitset
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0) # was bitset
    if not args.useProbeDiscri:
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x0)#change the results!!!!
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x0)


    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DAC)
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(QMin)
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(delay)

    
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

    pixel_data = acquire_data(top, useExt,QRange)


    if len(pixel_data) == 0 : raise ValueError('No hits were detected during delay sweep. Aborting!')    
    #if len(pixel_data['HitDataTOA']) != len(QRange) : raise ValueError('Missing Q points. Aborting!')

   #  #######################
   #  # Data Processing TOA #
   #  #######################
    #store mean and rms
    if os.path.exists(outFile+'.csv'):
       ts = str(int(time.time()))
       outFile = outFile+"_"+ts
    outFile = outFile+'.csv'
    ff = open(outFile,'a')
    
    #store raw
    outPickle=outFile.replace(".csv",".pkl")
    if os.path.exists(outPickle+'.pkl'):
       ts = str(int(time.time()))
       outPickle = outPickle+"_"+ts
    outPickle = outFile+'.pkl'
    pickle.dump((QRange,pixel_data),open(outPickle,"wb"))
  
    TOAMeanArray = np.zeros(len(QRange))
    TOARMSArray = np.zeros(len(QRange))
    TOTcMeanArray = np.zeros(len(QRange))
    TOTcRMSArray = np.zeros(len(QRange))

    TOTMeanArray = np.zeros(len(QRange))
    TOTRMSArray = np.zeros(len(QRange))


    QArray=np.array(QRange)*args.Qconv
    for iQ in range(len(QRange)):
       Q=QRange[iQ]
       print (Q,pixel_data['HitDataTOTc'][iQ])
       if len(pixel_data['HitDataTOA'])==0:
           print ("No data for Q=",QRange[iQ])
           continue
       TOAmean=np.mean(pixel_data['HitDataTOA'][iQ])*args.LSBTOA
       TOArms=np.std(pixel_data['HitDataTOA'][iQ])*args.LSBTOA
       TOTcmean=np.mean(pixel_data['HitDataTOTc'][iQ])
       TOTcrms=np.std(pixel_data['HitDataTOTc'][iQ])
       TOTfmean=np.mean(pixel_data['HitDataTOTf'][iQ])
       TOTfrms=np.std(pixel_data['HitDataTOTf'][iQ])
       TOTmean=(TOTcmean+1.)*args.LSBTOTc-TOTfmean*args.LSBTOTf
       TOTrms=math.sqrt(math.pow(TOTcrms*args.LSBTOTc,2)+math.pow(TOTfrms*args.LSBTOTf,2))

       if not math.isnan(TOAmean):TOAMeanArray[iQ]=TOAmean
       if not math.isnan(TOArms):TOARMSArray[iQ]=TOArms
       if not math.isnan(TOTcmean):TOTcMeanArray[iQ]=TOTcmean
       if not math.isnan(TOTcrms):TOTcRMSArray[iQ]=TOTcrms
       if not math.isnan(TOTmean):TOTMeanArray[iQ]=TOTmean
       if not math.isnan(TOTrms):TOTRMSArray[iQ]=TOTrms



       ff.write("%f,%f,%f,%f,%f,%f,%f,%f,%f,\n"%(QRange[iQ],TOAmean,TOArms,TOTcmean,TOTcrms,TOTfmean,TOTfrms,TOTmean,TOTrms))
       #print (np.mean(pixel_data['HitDataTOA'][iQ]),np.std(pixel_data['HitDataTOA'][iQ]))
       #print (np.mean(pixel_data['HitDataTOTc'][iQ]),np.std(pixel_data['HitDataTOTc'][iQ]))
       #print (np.mean(pixel_data['HitDataTOTc']),np.std(pixel_data['HitDataTOTc']))
    ff.close()
    print (QRange)
    print (TOAMeanArray)
    print (TOAMeanArray)


    
    ################Plotting
    QTitle="Q [dac]"
    TOTTitle="TOT [ps]"
    TOATitle="TOA [ps]"
    jitterTitle="Jitter [ps]"


    if args.Qconv!=1:
        QTitle="Q [fC]"
    if args.LSBTOA==1:
        TOATitle="TOA [dac]"
        jitterTitle="Jitter [dac]"
    if args.LSBTOTf==0 and args.LSBTOTc==1:
        TOTTitle="TOTc [dac]"
    if args.LSBTOTf==0 and args.LSBTOTc!=1:
        TOTTitle="TOTc [ps]"
            
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))
    
    # Plot (0,0) ; top left
    ax1.scatter(QArray, TOAMeanArray)
    ax1.grid(True)
    ax1.set_title('', fontsize = 11)
    ax1.set_xlabel(QTitle, fontsize = 10)
    ax1.set_ylabel(TOATitle, fontsize = 10)
    ax1.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
    ax1.set_ylim(bottom = 0, top = np.max(TOAMeanArray)*1.1)
    
   # Plot (0,1) ; top right
    ax2.scatter(QArray, TOARMSArray)
    ax2.grid(True)
    ax2.set_title('', fontsize = 11)
    ax2.set_xlabel(QTitle, fontsize = 10)
    ax2.set_ylabel(jitterTitle, fontsize = 10)
    ax2.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
    ax2.set_ylim(bottom = 0, top = np.max(TOARMSArray)*1.1)
   # Plot (1,0) ; bottom left
    
    ax3.scatter(QArray, TOTMeanArray)
    ax3.grid(True)
    ax3.set_title('', fontsize = 11)
    ax3.set_xlabel(QTitle, fontsize = 10)
    ax3.set_ylabel(TOTTitle, fontsize = 10)
    ax3.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
    ax3.set_ylim(bottom = 0, top = np.max(TOTMeanArray)*1.1)
    
    ax4.scatter( TOTMeanArray, TOAMeanArray)
    ax4.grid(True)
    ax4.set_title('', fontsize = 11)
    ax4.set_xlabel(TOTTitle, fontsize = 10)
    ax4.set_ylabel(TOATitle, fontsize = 10)
    ax4.set_xlim(left = np.min(TOTMeanArray)*0.9, right = np.max(TOTMeanArray)*1.1)
    ax4.set_ylim(bottom = 0, top = np.max(TOAMeanArray)*1.1)
  
    
   #  plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
    plt.show()
   #  #################################################################
    
    time.sleep(0.5)
    # Close
    top.stop()
    #################################################################




if __name__ == "__main__":
    args = parse_arguments()
    print(args)

    measureTimeWalk(args.ip, args.board, args.useExt,args.cfg, args.ch, args.QMin,args.QMax,args.QStep, args.DAC, args.delay, args.out)
