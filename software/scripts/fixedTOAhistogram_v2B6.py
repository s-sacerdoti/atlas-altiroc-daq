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
#script modified to have one delay/one threshold
#################################################################
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
import matplotlib.mlab as mlab
#from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
#################################################################
DebugPrint = True
#################################################################
# Set the argument parser
def parse_arguments():
    parser = argparse.ArgumentParser()

    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

    # Add arguments
    parser.add_argument("--ip", nargs = '+', required = True, help = "IP address")
    parser.add_argument("--cfg", type = str, required = False, default = 'config/config_v2B6_def.yml', help = "config file")
    parser.add_argument("--ch", type = int, required = True, help = "channel")
    parser.add_argument("--Q", type = int, required = True, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = True, help = "DAC vth")
    parser.add_argument("--delay", type = int, required = True, help = "DAC delay")
    parser.add_argument("--out", type = str, required = False, default = 'testTOA.txt', help = "output file")

    # Get the arguments
    args = parser.parse_args()
    return args
#################################################################
def setupRogue(argip,configFile):
    # Setup root class
    top = feb.Top(ip= argip, loadYaml= False)    
    
    # Start the system
    #top.start(initRead=True)
    
    # Load the default YAML file
    print(f'Loading {configFile} Configuration File...')
    top.LoadConfig(arg = configFile)
    #top.Asic.DoutDebug.ForwardData.set(0x0)
   
    if DebugPrint: 
        # Tap the streaming data interface (same interface that writes to file)
        dataStream = feb.PrintEventReader()
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA
    
    return top

#################################################################
def fixedTOAhistogram(top,argip,
        configFile,
        pixel_number,
        Qinj, #Pulser Decimal code with added resistance: 3 = 2.66,6 = 5.24, 12 =10.32 fC, 24=20.08 fC  ##
        DACvalue,
        DelayValue,
        outFile):

    NofIterations = 200  # <= Number of TOA measurements
    probePA = False

    LSBest = 28.64 #ch4
    if pixel_number == 9:
        LSBest = 30.4
    elif pixel_number == 14:
        LSBest = 31.28 #ps
    
    if top == None:
        top = setupRogue(argip,configFile)

    #################################################################
    # Pixel Readout Selection                                      ##
    top.Fpga[0].Asic.Probe.en_probe_pa.set(0x0)

    for i in range(25):
        top.Fpga[0].Asic.Probe.pix[i].probe_pa.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].probe_vthc.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].probe_dig_out_disc.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].probe_toa.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].probe_tot.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].totf.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].tot_overflow.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].toa_busy.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].Hit.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].tot_busy.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].tot_ready.set(0x0)
        top.Fpga[0].Asic.Probe.pix[i].en_read.set(0x0)

    if pixel_number in range(0, 5):
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x1)
        top.Fpga[0].Asic.Probe.EN_dout.set(0x1)
    if pixel_number in range(5, 10):
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x2)
        top.Fpga[0].Asic.Probe.EN_dout.set(0x2)
    if pixel_number in range(10, 15):
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x4)
        top.Fpga[0].Asic.Probe.EN_dout.set(0x4)
    if pixel_number in range(15, 20):
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x8)
        top.Fpga[0].Asic.Probe.EN_dout.set(0x8)
    if pixel_number in range(20, 25):
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x10)
        top.Fpga[0].Asic.Probe.EN_dout.set(0x10)

    #top.Fpga[0].Asic.Gpio.RSTB_READ.set(0x0)                           ##
    #time.sleep(0.1)                                            ##
    #top.Fpga[0].Asic.Gpio.RSTB_READ.set(0x1)                           ##
                                                               ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x0)         ## 
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_vthc.set(0x0)       ## 
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x1)#
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_toa.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_tot.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].totf.set(0x0)             ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_overflow.set(0x0)     ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].toa_busy.set(0x0)         ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].Hit.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_busy.set(0x0)         ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_ready.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].en_read.set(0x1)          ##
    #################################################################
    
    #################################################################
    # Custom Configuration                                         ##
    for i in range(25):                                        ##
        top.Fpga[0].Asic.SlowControl.disable_pa[i].set(0x1)            ##
        top.Fpga[0].Asic.SlowControl.ON_discri[i].set(0x0)             ##
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[i].set(0x1)            ##
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)           ##
        top.Fpga[0].Asic.SlowControl.ON_Ctest[i].set(0x0)              ##
                                                               ##
        top.Fpga[0].Asic.SlowControl.cBit_f_TOA[i].set(0x0)            ##
        top.Fpga[0].Asic.SlowControl.cBit_s_TOA[i].set(0x0)            ##      
        top.Fpga[0].Asic.SlowControl.cBit_f_TOT[i].set(0x0)            ##
        top.Fpga[0].Asic.SlowControl.cBit_s_TOT[i].set(0x0)            ##
        top.Fpga[0].Asic.SlowControl.cBit_c_TOT[i].set(0x0)            ##
                                                               ##
    for i in range(16):                                        ##
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)           ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)     ##
    top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)      ##
    top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)        ##
    top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)    ##
    top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)     ##
    top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)       ##
    top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(0x40)   ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.Write_opt.set(0x0)                    ##
    top.Fpga[0].Asic.SlowControl.Precharge_opt.set(0x0)                ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.DLL_ALockR_en.set(0x1)                ##
    top.Fpga[0].Asic.SlowControl.CP_b.set(0x5) #5                      ##
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlf_en.set(0x0) #1             ##
    top.Fpga[0].Asic.SlowControl.ext_Vcrtls_en.set(0x0) #1             ##
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlc_en.set(0x0) #1             ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.totf_satovfw.set(0x1)                 ##
    top.Fpga[0].Asic.SlowControl.totc_satovfw.set(0x1)                 ##
    top.Fpga[0].Asic.SlowControl.toa_satovfw.set(0x1)                  ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.SatFVa.set(0x3)                       ##
    top.Fpga[0].Asic.SlowControl.IntFVa.set(0x1)                       ##
    top.Fpga[0].Asic.SlowControl.SatFTz.set(0x4)                       ##
    top.Fpga[0].Asic.SlowControl.IntFTz.set(0x1)                       ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.cBitf.set(0x0) #0                     ##
    top.Fpga[0].Asic.SlowControl.cBits.set(0xf) #f                     ##
    top.Fpga[0].Asic.SlowControl.cBitc.set(0xf) #f                     ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0) #f  ##
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0) #0  ##
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf) #f  ##
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0) #0  ##
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf) #0  ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.Cp_Vpa.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cd[0].set(0x7) #6                     ## DON'T FORGET to change cd [] 0, 1 or 2 for ch4, 9 or 14                   ##
    top.Fpga[0].Asic.SlowControl.cd[1].set(0x7) #6                     ## DON'T FORGET to change cd [] 0, 1 or 2 for ch4, 9 or 14                   ##
    top.Fpga[0].Asic.SlowControl.cd[2].set(0x7) #6                     ## DON'T FORGET to change cd [] 0, 1 or 2 for ch4, 9 or 14                   ##
    top.Fpga[0].Asic.SlowControl.dac_biaspa.set(30) #10 30= 0x1e 60=0x3c ##
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj) #2= 5fC,7 =10 fC, 0x10=20 fC     0x23=40 fC       0x2D= 50 fC 0x30= 60 fC    ##
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(375)              ##
    
    #top.Asic.DoutDebug.DeserSampleEdge.set(0x0)                ##
                                                               ##
    #top.Asic.PulseTrain.PulseCount.set(0x1)                    ##
    #top.Asic.PulseTrain.PulseWidth.set(0x8)                    ##
    #top.Asic.PulseTrain.PulsePeriod.set(0x4)                   ##
    #top.Asic.PulseTrain.PulseDelay.set(0x4)                    ##
    #top.Asic.PulseTrain.ReadDelay.set(0x9)                     ##
    #top.Asic.PulseTrain.ReadDuration.set(0x70) #10a0           ##
    #top.Asic.PulseTrain.ResetCounterMask.set(0x3)              ##
    #top.Asic.PulseTrain.ResetTdcMask.set(0x2)                  ##
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(0x0)   # Rising edge of EXT_TRIG or CMD_PULSE delay
    top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0xfff) # Falling edge of EXT_TRIG (independent of CMD_PULSE)

    top.Fpga[0].Asic.Readout.StartPix.set(pixel_number)
    top.Fpga[0].Asic.Readout.LastPix.set(pixel_number)

                                                               ##
    #################################################################
    
    #################################################################
    ## Data Stream Alignment                                        ##
    #                                                               ##
    #top.Asic.PulseTrain.Continuous.set(0x0)                        ##
    #top.Asic.Gpio.RSTB_TDC.set(0x0)                                ##
    #Write_opt = top.Asic.SlowControl.Write_opt.get()               ##
    #Precharge_opt = top.Asic.SlowControl.Precharge_opt.get()       ##  
    #top.Asic.SlowControl.Write_opt.set(0x0)                        ##
    #top.Asic.SlowControl.Precharge_opt.set(0x0)                    ##
    #time.sleep(0.1)                                                ##
    #top.Asic.PulseTrain.ResetCounterPolarity.set(0x1)              ##
    #top.Asic.PulseTrain.Continuous.set(0x1)                        ##
    #time.sleep(0.1)                                                ##
    #top.Asic.SlowControl.Write_opt.set(Write_opt)                  ##
    #top.Asic.SlowControl.Precharge_opt.set(Precharge_opt)          ##
    #top.Asic.Gpio.RSTB_TDC.set(0x1)                                ##
    #top.Asic.PulseTrain.ResetCounterPolarity.set(0x0)              ##
    #top.Asic.PulseTrain.Continuous.set(0x0)                        ##
    #time.sleep(0.1)                                                ##
    #################################################################
    
    #################################################################
    ##### Data Acquisition TOA                                         ##
    #################################################################
                                                                   ##
    print ('Delay =',DelayValue)                                    ##
    
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(DelayValue)                                                       ##
    #top.SysReg.DlyData.set(DelayValue)                              ##
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DACvalue)              ##
    
    filename = 'TestData/TOA%d.dat' %DelayValue                                                       ##
    try:                                                   ##
        os.remove(filename)
    except OSError:
        pass    
                           
    top.dataWriter._writer.open(filename)   ##
    #top.Fpga[0].Asic.DoutDebug.ForwardData.set(0x1)                ##
    time.sleep(0.1)                                                ##
    for j in range(NofIterations):                      ##
                                                           ##
        top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)                    ##
        top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)                    ##
        time.sleep(0.01)                                   ##
        #top.Asic.PulseTrain.OneShot()                      ##
        top.Fpga[0].Asic.CalPulse.Start()
                                                           ##
    #top.Fpga[0].Asic.DoutDebug.ForwardData.set(0x0)                ##
    top.dataWriter._writer.close()                         ##
    #################################################################
    ######### Data Processing TOA
    #################################################################
    HitDataTOA = []
    HitDataTOA_ps = []
    
    #Delay = []
    HitCnt = []
    DataMean = []
    DataStdev = []
    
    #for i in range(DelayRange):
    # Create the File reader streaming interface
    dataReader = rogue.utilities.fileio.StreamReader()
    time.sleep(0.01)
    # Create the Event reader streaming interface
    dataStream = feb.MyFileReader()
    time.sleep(0.01)
    # Connect the file reader to the event reader
    pr.streamConnect(dataReader, dataStream) 
    time.sleep(0.01)
    # Open the file
    dataReader.open(filename)
    time.sleep(0.01)
    # Close file once everything processed
    dataReader.closeWait()
    time.sleep(0.01)
    
    try:
        print('Processing Data for Delay = %d...' % DelayValue)
    except OSError:
        pass  
    
    HitData = dataStream.HitData
    HitDataTOA = HitData
    #print(HitDataTOA)
    
    HitCnt.append(len(HitData))
    if len(HitData) > 0:
        DataMean.append(np.mean(HitData, dtype=np.float64))
        DataStdev.append(math.sqrt(math.pow(np.std(HitData, dtype=np.float64),2)+1/12))
        print('got hits ')
        index = np.where(np.sort(DataStdev))
        MeanDataStdev = np.mean(np.sort(DataStdev)[index[0][0]:len(np.sort(DataStdev))])
    
    else:
        DataMean.append(0)
        DataStdev.append(0)
        print('######  No events fund!!  #######')
        index = 0
        MeanDataStdev = 0
    
    #print(HitDataTOA)
    #################################################################
    # Plot Data
    #################################################################
    logFile='logCH'+str(pixel_number)+'_Q'+str(Qinj)+'Vth'+str(DACvalue)+'del'+str(DelayValue)+'.txt'
    #break if too few hits
    if len(HitDataTOA) < NofIterations*0.01:
        print('Less than 5% of events had hits, try again!')
        top.stop()
        flog = open('/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/TDC/'+logFile,'a')
        flog.write(str(int(time.time()))+'  0  0'+'\n')
        flog.close()
        return 
    
    else:
        HitDataTOA_ps = [ x * LSBest for x in HitDataTOA]
        #get mean and sigma w/o first measurement, which is always noisy
        TOAmean = np.mean(HitDataTOA_ps[1:], dtype=np.float64)
        TOAsigma = np.std(HitDataTOA_ps[1:], dtype=np.float64)
        
        ## choose binning
        minBin =  min(HitDataTOA_ps)
        maxBin =  max(HitDataTOA_ps)
        mybins = []
        auxB = minBin-2*LSBest
        auxN = 0
        while auxB < maxBin:
            auxB=auxB+LSBest
            mybins.append(auxB)
            auxN=auxN+1
        mybins.append(auxB+LSBest)
        mybins.append(auxB+2*LSBest)
        
        print('mean value',TOAmean)
        print('sigma ',TOAsigma)
        print('Number of events = ',len(HitDataTOA))
        #plots histogram
        y, bins, p = plt.hist(HitDataTOA_ps,  bins= mybins, align = 'left', edgecolor = 'k', color = 'royalblue')
        
        x = bins[:len(bins)-1]
        #for i in range(0,len(bins)-1):
        #    x.append((bins[i+1]+bins[i])/2)
        #print(len(x),"  x  =",x)
        #print(len(y),"  y  =",y)
        
        plt.plot(x,y,'b+:',label='data')
        plt.legend()
        
        plt.savefig(outFile+'.png')
        #plt.show()
    
    #################################################################
    # Save Data
    #################################################################
    ff = open(outFile+'.txt','a')
    ff.write('Long TOA measurement scan ---- '+time.ctime()+'\n')
    ff.write('Pixel = '+str(pixel_number)+'\n')
    ff.write('config file = '+configFile+'\n')
    ff.write('NofIterations = '+str(NofIterations)+'\n')
    ff.write('cmd_pulser = '+str(Qinj)+'\n')
    ff.write('Delay DAC = '+str(DelayValue)+'\n')
    ff.write('LSBest = '+str(LSBest)+'\n')
    ff.write('Threshold = '+str(DACvalue)+'\n')
    ff.write('N hits = '+str(HitCnt)+'\n')
    ff.write('Number of events = '+str(len(HitDataTOA))+'\n')
    ff.write('mean value = '+str(TOAmean)+'\n')
    ff.write('sigma = '+str(TOAsigma)+'\n')
    ff.write('TOAvalues = '+str(HitDataTOA)+'\n')
    ff.write('\n')
    ff.close()

    print('Saved file '+outFile)

    #For quick plot of TOA and Jitter
    flog = open('/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/TDC/'+logFile,'a')
    flog.write(str(int(time.time()))+'  '+ str(TOAmean)+' '+str(TOAsigma)+'\n')
    flog.close()
    
    
    time.sleep(0.5)
    # Close
    top.stop()

    return [TOAmean, TOAsigma]
#################################################################
#################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)
    fixedTOAhistogram(None,args.ip,args.cfg,args.ch,args.Q,args.DAC,args.delay,args.out)

