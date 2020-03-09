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
from setASICconfig import *                                    ##
#################################################################
#script settings
LSBest = 20
#args.N = 20  # <= Number of Iterations for each Vth
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
    config_file = 'config/asic_config_B4.yml'
    minDAC = 280
    maxDAC = 420
    DACstep = 5
    DelayValue = 2400
    Rin_Vpa=0 # 0 => 25K, 1 => 15 K
    Vthc=-1
    
    # Add arguments
    parser.add_argument( "--allChON", type = argBool, required = False, default = False, help = "")
    parser.add_argument( "--allCtestON", type = argBool, required = False, default = False, help = "")        
    parser.add_argument("--Vthc", type = int, required = False, default = Vthc, help = "Vth cor")
    parser.add_argument("--Rin_Vpa", type = int, required = False, default = Rin_Vpa, help = "RinVpa")
    parser.add_argument( "--readAllChannels", type = argBool, required = False, default = False, help = " read all channels")
    parser.add_argument("--Cd", type = int, required = False, default = -1, help = "Cd")
    parser.add_argument("--N","-N", type = int, required = False, default = 100, help = "Nb of events")
    parser.add_argument("--ip", nargs ='+', required = False, default = ['192.168.1.10'], help = "List of IP address")
    parser.add_argument( "--board", type = int, required = False, default = 7,help = "Choose board")
    parser.add_argument( "--autoStop", type = argBool, required = False, default = False, help = "show plots")
    parser.add_argument( "--display", type = argBool, required = False, default = True, help = "          ")
    parser.add_argument( "--debug", type = argBool, required = False, default = True, help = "debug")
    parser.add_argument( "--useProbePA", type = argBool, required = False, default = False, help = "use probe PA")
    parser.add_argument( "--useProbeDiscri", type = argBool, required = False, default = False, help = "use probe Discri")
    parser.add_argument( "--checkOFtoa", type = argBool, required = False, default = True, help = "check TOA overflow")
    parser.add_argument( "--checkOFtot", type = argBool, required = False, default = True, help = "check TOT overflow")
    parser.add_argument("--cfg", type = str, required = False, default = None, help = "config file")
    parser.add_argument("--ch", type = int, required = False, default = pixel, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = Qinj, help = "injected charge DAC")
    parser.add_argument("--delay", type = int, required = False, default = DelayValue, help = "delay")
    parser.add_argument("--minVth", type = int, required = False, default = minDAC, help = "scan start")
    parser.add_argument("--maxVth", type = int, required = False, default = maxDAC, help = "scan stop")
    parser.add_argument("--VthStep", type = int, required = False, default = DACstep, help = "scan step")
    parser.add_argument("--out", type = str, required = False, default = 'testThreshold.txt', help = "output file name")  
    parser.add_argument( "--skipExistingFile", type = argBool, required = False, default = False, help = "")

    
    # Get the arguments
    
    extra=""
    args = parser.parse_args()
    if args.allChON:
        extra+="allChON"
    if args.allCtestON:
        extra+="allCtestON"
    args.out='%sthres_B_%d_rin_%d_ch_%d_cd_%d_delay_%d_Q_%d_%s'%(args.out,args.board,args.Rin_Vpa,args.ch,args.Cd,args.delay,args.Q,extra)
    return args

##############################################################################
def acquire_data(dacScan, top, n_iterations,autoStop=False,readAllData=False): 
    pixel_stream = feb.PixelReader() 
    if readAllData:
        pixel_stream.channelNumber=chNb #ALLDATA
        pixel_stream.doPrint=True #ALLDATA
    pixel_stream.checkOFtoa=args.checkOFtoa
    pixel_stream.checkOFtot=args.checkOFtot 
   
    pyrogue.streamTap(top.dataStream[0], pixel_stream) # Assuming only 1 FPGA
    pixel_data = {
    'HitDataTOA' : [],
    'TOAOvflow' : []
    }
    
    asicVersion = 2 #hardcoded for now...
    effList=[]
    newDacScan=[]
    for scan_value in dacScan:
        
        if autoStop:
            nForCheck=10
            if len(effList)>        nForCheck:
                if(max(effList)>=0.5 and  all(np.array(effList[-nForCheck:])<0.05)):
                    break
                #used to remove saturated toa
            #print(toto)
        newDacScan.append(scan_value)

            
        print('Vth DAC = %d' %scan_value) 
        top.Fpga[0].Asic.SlowControl.DAC10bit.set(scan_value)
        top.initialize()#You MUST call this function after doing ASIC configurations!!!
            
        for iteration in range(n_iterations):
            if (asicVersion == 1): 
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.01)
                if readAllData:time.sleep(0.009)#ALLDATA
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)
                if readAllData:time.sleep(0.009)#ALLDATA

        print ("--> N = ",len(pixel_stream.HitDataTOA.copy()))
        effList.append(len(pixel_stream.HitDataTOA.copy())/n_iterations)
        pixel_data['HitDataTOA'].append( pixel_stream.HitDataTOA.copy() )
        pixel_data['TOAOvflow'].append( pixel_stream.TOAOvflow.copy() )
        while pixel_stream.count < args.N: pass
        pixel_stream.clear()
    
    return pixel_data,newDacScan

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


    
    if args.skipExistingFile and os.path.exists(outFile+'.txt'):
        print ('output file already exist. Skip......')
        sys.exit()

    #dac range    
    dacScan = range(minDAC,maxDAC,DACstep)

    #choose config file:
    if args.cfg==None:
        Configuration_LOAD_file = 'config/asic_config_B'+str(board)+'.yml'


    # Setup root class
    top = feb.Top(ip = argip, userYaml = [Configuration_LOAD_file])
    
    if args.debug:
        top.Fpga[0].AxiVersion.printStatus()
        # Tap the streaming data interface (same interface that writes to file)
        dataStream = feb.PrintEventReader()    
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA
    
    # Testing resets (why???)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)
    
    #configuration
    set_pixel_specific_parameters(top, pixel_number,args)

    #some more config
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(DelayValue)
    #top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0)
    #top.Fpga[0].Asic.CalPulse.CalPulseDelay.set(5000)
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj)

        
    #You MUST call this function after doing ASIC configurations!!!
    top.initialize()

    print   (top.Fpga[0].Asic.SlowControl.Rin_Vpa.value())
    
    #################################################################
    # Data Processing
    pixel_data,newDacScan = acquire_data(dacScan, top, args.N,args.autoStop)
    
    #################################################################
    # Data Processing
    
    HitCnt = []
    HitCnt2 = []
    TOAmean = []
    TOAjit = []
    TOAmean_ps = []
    TOAjit_ps = []
    allTOA = []

    num_valid_TOA_reads = len(pixel_data['HitDataTOA'])
    if num_valid_TOA_reads == 0:
        raise ValueError('No hits were detected during delay sweep. Aborting!')
    
    for idac,dacval in enumerate(newDacScan):
        #if checkOvF:
        #    overflow = np.array(pixel_data['TOAOvflow'][idac])
        #    no_ovf_id = np.where(overflow == 0)[0]
        #    HitDataTOA = [pixel_data['HitDataTOA'][idac][i] for i in no_ovf_id]
        #    HitCnt.append(len(HitDataTOA))
        #    allTOA.append(HitDataTOA)
        #else: 
        HitDataTOA = np.array(pixel_data['HitDataTOA'][idac])
        HitCnt.append(len(HitDataTOA))
        HitCnt2.append(np.count_nonzero(np.array(HitDataTOA)<127))






        
        allTOA.append(HitDataTOA)
        if len(HitDataTOA) > 0:
            okTOA=HitDataTOA!=127 #used to remove saturated toa
            TOAmean.append(np.mean(HitDataTOA[okTOA]))
            TOAjit.append(math.sqrt(math.pow(np.std(HitDataTOA[okTOA], dtype=np.float64),2)+1/12))
            TOAmean_ps.append(np.mean(HitDataTOA[okTOA], dtype=np.float64)*LSBest)
            TOAjit_ps.append(math.sqrt(math.pow(np.std(HitDataTOA[okTOA], dtype=np.float64),2)+1/12)*LSBest)
    
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
    # Print Data    #find min th, max th, and middle points:
    maxTH = 999
    suspicious=0
    for dac_index, dac_value in enumerate(newDacScan):
        if args.debug:
            try:
                print('Threshold = %d, HitCnt = %d/%d' % (dac_value, HitCnt[dac_index], args.N))
            except OSError:
                pass


        if dac_index>1 and HitCnt[dac_index]/args.N>0.95 and HitCnt2[dac_index]>0:
            #if dac_index
            maxTH = newDacScan[dac_index]
            suspicious=HitCnt2[dac_index]/float(args.N)
            print (maxTH,suspicious)
            

    
    # th25= (maxTH-minTH)*0.25+minTH
    # th50= (maxTH-minTH)*0.5+minTH
    # th75= (maxTH-minTH)*0.75+minTH

    print ("**************************************")
    print (suspicious)
    thresFlag="ok"
    if suspicious==0:
        print ("Can't find a threshold")
    elif suspicious>0.8:
        print('Threshold = %d '% (maxTH))
    else:
        print('Threshold = %d but LARGE FRAC OF TOA 127 (%f)'% (maxTH,1-suspicious))
        thresFlag="PRB!!!!!!!!!"
    print ("**************************************")
    #print('Found minTH = %d, maxTH = %d  - points at 0.25, 0.50 and 0.75 are %d,%d,%d'% (minTH,maxTH,th25,th50,th75))
    #print('First DAC with efficiency below 60% = ', th50percent)

    if os.path.exists(outFile+'.txt'):
       ts = str(int(time.time()))
       outFile = outFile+"_"+ts
    outFile+=".txt"
    ff = open(outFile,'a')


    ff.write('dacList[(%d,%d,%d)]=%d#%d,%.2f,%s \n'%(args.board,pixel_number,args.Cd,maxTH,Qinj,round(suspicious,2),thresFlag))

    
    # ff.write('Threshold scan ----'+time.ctime()+'\n')
    # ff.write('Pixel = '+str(pixel_number)+'\n')
    # #ff.write('column = '+hex(column)+'\n')
    # ff.write('config file = '+Configuration_LOAD_file+'\n')
    # ff.write('args.N = '+str(args.N)+'\n')
    # #ff.write('dac_biaspa = '+hex(dac_biaspa)+'\n')
    # ff.write('cmd_pulser = '+str(Qinj)+'\n')
    # ff.write('LSBest = '+str(LSBest)+'\n')
    # ff.write('Cd ='+str(cd*0.5)+' fC'+'\n')
    # #ff.write('Found minTH = %d, maxTH = %d - points at 0.25, 0.50 and 0.75 are %d,%d,%d \n'% (minTH,maxTH,th25,th50,th75))
    # ff.write('First DAC with efficiency below 0.6 = %d  \n' % (th50percent))
    # ff.write('Threshold = '+str(newDacScan)+'\n')
    # ff.write('N hits = '+str(HitCnt)+'\n')
    # ff.write('Mean TOA = '+str(TOAmean)+'\n')
    # ff.write('Std Dev TOA = '+str(TOAjit)+'\n')
    # ff.write('MeanTOAps = '+str(TOAmean_ps)+'\n')
    # ff.write('StdDevTOAps = '+str(TOAjit_ps)+'\n')
    # ff.write('dacVth   TOA N_TOA'+'\n')

    for dac_index, dac_value in enumerate(newDacScan):
        ff.write(str(dac_value)+' '+str(args.N)+' '+str(HitCnt[dac_index])+' '+str(HitCnt2[dac_index])+'\n')
        #for itoa in range(len(allTOA[dac_index])):
        #    ff.write(str(dac_value)+' '+str(allTOA[dac_index][itoa])+' '+str(len(allTOA[dac_index]))+'\n')

    ff.close()

    #################################################################
    #
    #################################################################
    print ("-------------------------------------------------------")
    print("The arguments was:")
    print(args)
    print("Config file was:", Configuration_LOAD_file)
    printStatus(top)
    print ("-------------------------------------------------------")
    
    #################################################################
    #################################################################
    ## Plot Data

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))

    #plot N events vs threshold
    ax1.scatter(newDacScan,HitCnt)
    ax1.scatter(newDacScan,HitCnt2, facecolors='none', edgecolors='r')
    #ax1.scatter(newDacScan,HitCnt)
    ax1.set_title('Number of hits vs Threshold', fontsize = 11)
    ax1.set_xlabel('Threshold DAC', fontsize = 10)
    ax1.set_ylabel('Number of TOA hits', fontsize = 10)

    #plot TOA vs threshold
    ax2.scatter(newDacScan,TOAmean_ps)
    ax2.set_title('Mean TOA vs Threshold', fontsize = 11)
    ax2.set_xlabel('Threshold DAC', fontsize = 10)
    ax2.set_ylabel('Mean TOA value [ps]', fontsize = 10)

    #plot jitter vs Threshold
    ax3.scatter(newDacScan ,TOAjit_ps)
    ax3.set_title('Jitter TOA vs Threshold', fontsize = 11)
    ax3.legend(['Average Std. Dev. = %f ps' % (jitterMean*LSBest)], loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax3.set_xlabel('Threshold DAC', fontsize = 10)
    ax3.set_ylabel('Mean TOA Jitter', fontsize = 10)
    ax3.set_ylim(bottom = 0, top = 100)
               
    plt.subplots_adjust(hspace = 0.35, wspace = 0.2)
    plt.savefig(outFile+".pdf")
    if args.display:
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

    

