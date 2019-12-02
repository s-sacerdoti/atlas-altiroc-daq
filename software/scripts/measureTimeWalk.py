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


#################################################################
# 
#################################################################
def acquire_data(top, useExt,QRange): 
    pixel_stream = feb.PixelReader()
    #pixel_stream.checkOFtoa=False
    #pixel_stream.checkOFtot=True   
    pixel_stream.checkOFtoa=args.checkOFtoa
    pixel_stream.checkOFtot=args.checkOFtot 
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

        Nevts=args.N
        if args.moreStatAtLowQ and Q_value<=8:
            Nevts*=5
        for pulse_iteration in range(Nevts):
            top.Fpga[0].Asic.CalPulse.Start()
            time.sleep(0.001)

            
        pixel_data['HitDataTOA'].append( pixel_stream.HitDataTOA.copy() )
        if args.ch<15:
            pixel_data['HitDataTOTf'].append( pixel_stream.HitDataTOTf_vpa.copy() )
            pixel_data['HitDataTOTc'].append( pixel_stream.HitDataTOTc_vpa.copy() )
        else:
            pixel_data['HitDataTOTf'].append( pixel_stream.HitDataTOTf_tz.copy() )
            pixel_data['HitDataTOTc'].append( pixel_stream.HitDataTOTc_tz.copy() )



        
        
        while pixel_stream.count < args.N: pass
        pixel_stream.clear()

    return pixel_data


#################################################################
# 
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
    Vthc=0x40   
    Rin_Vpa=0 # 0 => 25K, 1 => 15 K


    # Add arguments
    parser.add_argument("--Vthc", type = int, required = False, default = Vthc, help = "Vth cor")
    parser.add_argument("--Rin_Vpa", type = int, required = False, default = Rin_Vpa, help = "RinVpa")

    parser.add_argument( "--ip", nargs ='+', required = False, default = ['192.168.1.10'], help = "List of IP addresses")
    parser.add_argument( "--board", type = int, required = False, default = 7,help = "Choose board")
    parser.add_argument( "--display", type = argBool, required = False, default = True, help = "show plots")
    parser.add_argument( "--debug", type = argBool, required = False, default = True, help = "debug")
    parser.add_argument( "--moreStatAtLowQ", type = argBool, required = False, default = True, help = "increase statistics for low Q")
    parser.add_argument( "--morePointsAtLowQ", type = argBool, required = False, default = False, help = "increase statistics for low Q")
    
    parser.add_argument( "--skipExistingFile", type = argBool, required = False, default = False, help = "")
        
    parser.add_argument( "--useProbePA", type = argBool, required = False, default = False, help = "use probe PA")
    parser.add_argument( "--useProbeDiscri", type = argBool, required = False, default = False, help = "use probe Discri")
    parser.add_argument( "--checkOFtoa", type = argBool, required = False, default = True, help = "check TOA overflow")
    parser.add_argument( "--checkOFtot", type = argBool, required = False, default = True, help = "check TOT overflow")
    parser.add_argument( "--useExt", type = argBool, required = False, default = False,help = "Use external trigger")
    parser.add_argument( "--cfg", type = str, required = False, default = None, help = "Select yml configuration file to load")  
    parser.add_argument("--ch", type = int, required = False, default = pixel_number, help = "channel")
    parser.add_argument("-N", type = int, required = False, default = 50, help = "Nb of events")
    parser.add_argument("--Cd", type = int, required = False, default = -1, help = "Cd")
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
    args.out='%sTW_B_%d_rin_%d_ch_%d_cd_%d_delay_%d_thres_%d_'%(args.out,args.board,args.Rin_Vpa,args.ch,args.Cd,args.delay,args.DAC)
    print(args.out)
    print(outFile)


    return args




#################################################################
# 
#################################################################
def writeData(f,iQ,Q,key,theMap):
    f.write("%s,%s"%(Q,key))
    for toa in theMap[key][iQ]:
        f.write(",%f"%(toa))
    f.write("\n")

#################################################################
# 
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


    if args.skipExistingFile and os.path.exists(outFile+'.csv'):
        print ('output file already exist. Skip......')
        sys.exit()



    
    #list of charge for looping
    QRange = list(range( QMin, QMax, QStep ))
    if args.morePointsAtLowQ:
        if 13 not in QRange: QRange=[13]+QRange
        if 11 not in QRange: QRange=[11]+QRange	
        #if 10 not in QRange: QRange=[10]+QRange	
        if 9 not in QRange: QRange=[9]+QRange
        #if 8 not in QRange: QRange=[8]+QRange
        if 7 not in QRange: QRange=[7]+QRange
        #if 6 not in QRange: QRange=[6]+QRange




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

    # Testing resets
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)

    # Set parameters
    set_pixel_specific_parameters(top, pixel_number)
    if pixel_number in range(0, 5): bitset=0x1
    if pixel_number in range(5, 10): bitset=0x2
    if pixel_number in range(10, 15): bitset=0x4
    if pixel_number in range(15, 20): bitset=0x8
    if pixel_number in range(20, 25): bitset=0x10
    for ipix in range(0,25):top.Fpga[0].Asic.Probe.pix[ipix].probe_pa.set(0x0)
    if not args.useProbePA:
        top.Fpga[0].Asic.Probe.en_probe_pa.set(0x0) 
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x0)
    else:
        top.Fpga[0].Asic.Probe.en_probe_pa.set(bitset) 
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x1)
    for ipix in range(0,25):top.Fpga[0].Asic.Probe.pix[ipix].probe_dig_out_disc.set(0x0)
    if not args.useProbeDiscri:
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x0) 
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x0)
    else:
        top.Fpga[0].Asic.Probe.en_probe_dig.set(bitset) 
        top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x1)
        
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DAC)
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(QMin)
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(delay)

    # Data Acquisition for TOA with external
    if useExt:
        print("Will use external trigger")
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x0)
 
    # Overright Cd
    if args.Cd>=0:
        for i in range(5):
            top.Fpga[0].Asic.SlowControl.cd[i].set(args.Cd)  

    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(args.Rin_Vpa)
    top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(args.Vthc) # alignment

    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()

    # get data
    pixel_data = acquire_data(top, useExt,QRange)
    if len(pixel_data) == 0 : raise ValueError('No hits were detected during delay sweep. Aborting!')    


    #######################
    # Data Processing TOA #
    #######################
    #store mean and rms
    if os.path.exists(outFile+'.csv'):
       ts = str(int(time.time()))
       outFile = outFile+"_"+ts
    outFile = outFile+'.csv'
    ff = open(outFile,'a')
    
    #store raw
    outPickle=outFile.replace(".csv",".pkl")
    #pickle.dump((QRange,pixel_data),open(outPickle,"wb"))
    outData=outFile.replace(".csv",".data")
    ffData = open(outData,'a')



    TOAoffracArray = np.zeros(len(QRange))
    TOAMeanArray = np.zeros(len(QRange))
    TOARMSArray = np.zeros(len(QRange))
    TOTcMeanArray = np.zeros(len(QRange))
    TOTcRMSArray = np.zeros(len(QRange))

    TOTMeanArray = np.zeros(len(QRange))
    TOTRMSArray = np.zeros(len(QRange))


    QArray=np.array(QRange)*args.Qconv
    for iQ in range(len(QRange)):
       Q=QRange[iQ]
       #print (Q,pixel_data['HitDataTOTc'][iQ])
       if len(pixel_data['HitDataTOA'])==0:
           print ("No data for Q=",QRange[iQ])
           continue


       
       writeData(ffData,iQ,Q,"HitDataTOA",pixel_data)       
       writeData(ffData,iQ,Q,"HitDataTOTc",pixel_data)       
       writeData(ffData,iQ,Q,"HitDataTOTf",pixel_data)

       #fraction of saturated toa
       toaof=0
       for ele in  pixel_data['HitDataTOA'][iQ]:
           if ele==127:toaof+=1
       if len(pixel_data['HitDataTOA'][iQ])>0:
           TOAoffrac= toaof/float(len(pixel_data['HitDataTOA'][iQ]))
       else:
           TOAoffrac=1
           pass


       okTOA=np.array(pixel_data['HitDataTOA'][iQ])!=127 #used to remove saturated toa
       okTOTc=np.array(pixel_data['HitDataTOA'][iQ])!=127 #used to remove saturated toa




       
       TOAmean=np.mean(np.array(pixel_data['HitDataTOA'][iQ])[okTOA])*args.LSBTOA
       TOArms=np.std(np.array(pixel_data['HitDataTOA'][iQ])[okTOA])*args.LSBTOA
       TOTcmean=np.mean(np.array(pixel_data['HitDataTOTc'][iQ])[okTOTc])
       TOTcrms=np.std(np.array(pixel_data['HitDataTOTc'][iQ])[okTOTc])
       TOTfmean=np.mean(np.array(pixel_data['HitDataTOTf'][iQ])[okTOA])
       TOTfrms=np.std(np.array(pixel_data['HitDataTOTf'][iQ])[okTOA])
       if args.ch<15:
           TOTmean=(TOTcmean+1.)*args.LSBTOTc-TOTfmean*args.LSBTOTf
       else:
           TOTmean=(TOTcmean+1.)*args.LSBTOTc-TOTfmean*20
       TOTrms=math.sqrt(math.pow(TOTcrms*args.LSBTOTc,2)+math.pow(TOTfrms*args.LSBTOTf,2))

       if not math.isnan(TOAoffrac):TOAoffracArray[iQ]=TOAoffrac
       if not math.isnan(TOAmean):TOAMeanArray[iQ]=TOAmean
       if not math.isnan(TOArms):TOARMSArray[iQ]=TOArms
       if not math.isnan(TOTcmean):TOTcMeanArray[iQ]=TOTcmean
       if not math.isnan(TOTcrms) and  not math.isnan(TOTcmean) and TOTcmean>0:TOTcRMSArray[iQ]=TOTcrms/TOTcmean
       if not math.isnan(TOTmean):TOTMeanArray[iQ]=TOTmean
       if not math.isnan(TOTrms):TOTRMSArray[iQ]=TOTrms



       ff.write("%f,%f,%f,%f,%f,%f,%f,%f,%f,\n"%(QRange[iQ],TOAmean,TOArms,TOTcmean,TOTcrms,TOTfmean,TOTfrms,TOTmean,TOTrms))
       #print (np.mean(pixel_data['HitDataTOA'][iQ]),np.std(pixel_data['HitDataTOA'][iQ]))
       #print (np.mean(pixel_data['HitDataTOTc'][iQ]),np.std(pixel_data['HitDataTOTc'][iQ]))
       #print (np.mean(pixel_data['HitDataTOTc']),np.std(pixel_data['HitDataTOTc']))
    ff.close()
    ffData.close()
    #print (QRange)
    #print (TOAMeanArray)
    #print (TOAMeanArray)

    #################################################################
    #
    #################################################################
    print ("-------------------------------------------------------")
    print("The arguments was:")
    print(args)
    print("Config file was:", Configuration_LOAD_file)
    print ("-------------------------------------------------------")

    #################################################################
    #Plotting
    #################################################################
    if True:

        QTitle="Q [dac]"
        TOTTitle="TOT [ps]"
        TOTcTitle="TOTc [dac]"
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

        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(nrows = 3, ncols = 2, figsize=(13,9))

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

        ax3.scatter(QArray, TOTcMeanArray)
        ax3.grid(True)
        ax3.set_title('', fontsize = 11)
        ax3.set_xlabel(QTitle, fontsize = 10)
        ax3.set_ylabel(TOTcTitle, fontsize = 10)
        ax3.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
        ax3.set_ylim(bottom = 0, top = np.max(TOTcMeanArray)*1.1)

        ax4.scatter( QArray, TOTcRMSArray)
        ax4.grid(True)
        ax4.set_title('', fontsize = 11)
        ax4.set_xlabel(QTitle, fontsize = 10)
        ax4.set_ylabel("RMS(TOTc)/<TOTc>", fontsize = 10)
        ax4.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
        ax4.set_ylim(bottom = 0, top = np.max(TOTcRMSArray)*1.1)

        ax5.scatter(QArray, TOAoffracArray)
        ax5.grid(True)
        ax5.set_title('', fontsize = 11)
        ax5.set_xlabel(QTitle, fontsize = 10)
        ax5.set_ylabel("Saturated TOA frac", fontsize = 10)
        ax5.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
        ax5.set_ylim(bottom = 0, top = 1.1)

        ax6.scatter( TOTcMeanArray, TOAMeanArray)
        ax6.grid(True)
        ax6.set_title('', fontsize = 11)
        ax6.set_xlabel(TOTcTitle, fontsize = 10)
        ax6.set_ylabel(TOATitle, fontsize = 10)
        ax6.set_xlim(left = np.min(TOTMeanArray)*0.9, right = np.max(TOTcMeanArray)*1.1)
        ax6.set_ylim(bottom = 0, top = np.max(TOAMeanArray)*1.1)
        
        # ax6.scatter(QArray, TOTcMeanArray)
        # ax6.grid(True)
        # ax6.set_title('', fontsize = 11)
        # ax6.set_xlabel(QTitle, fontsize = 10)
        # ax6.set_ylabel(TOTcTitle, fontsize = 10)
        # ax6.set_xlim(left = np.min(QArray)*0.9, right = np.max(QArray)*1.1)
        # ax6.set_ylim(bottom = 0, top = np.max(TOTcMeanArray)*1.1)

       #  plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
        plt.savefig(outFile.replace(".csv",".pdf"))
        if args.display:plt.show()
       #  #################################################################

        time.sleep(0.5)
        # Close
        top.stop()
        #################################################################

    else:
       
        top.stop()
        #sys.exit()

if __name__ == "__main__":
    args = parse_arguments()
    print(args)

    measureTimeWalk(args.ip, args.board, args.useExt,args.cfg, args.ch, args.QMin,args.QMax,args.QStep, args.DAC, args.delay, args.out)