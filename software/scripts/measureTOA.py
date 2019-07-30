#!/usr/bin/env python3
##############################################################################
## This file is based on 'ATLAS ALTIROC DEV'.

##############################################################################
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
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

from configure_Board7 import *
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
    config_file = 'config/config_v2B6_noPAprobe.yml'
    dlyMin = 2250 
    dlyMax = 2700 
    dlyStep = 10
    
    
    # Add arguments
    parser.add_argument("--ip", type = str, required = True, help = "IP address")  
    parser.add_argument("--cfg", type = str, required = False, default = config_file, help = "config file")
    parser.add_argument("--ch", type = int, required = False, default = pixel, help = "channel")
    parser.add_argument("--Q", type = int, required = False, default = Qinj, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = False, default = DAC_Vth, help = "DAC vth")
    parser.add_argument("--delayMin", type = int, required = False, default = dlyMin, help = "scan start")
    parser.add_argument("--delayMax", type = int, required = False, default = dlyMax, help = "scan stop")
    parser.add_argument("--delayStep", type = int, required = False, default = dlyStep, help = "scan step")
    
    # Get the arguments
    args = parser.parse_args()
    return args

##############################################################################
def set_fpga_for_custom_config(top):
    top.Fpga[0].Asic.Probe.en_probe_pa.set(0x1)
    
    #first set all to 0
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

    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x1)         ## 
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
    
    BC = getBoardConfig()
    for i in range(25):
        top.Fpga[0].Asic.SlowControl.disable_pa[i].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[i].set(0x1)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.ON_Ctest[i].set(0x0)

        top.Fpga[0].Asic.SlowControl.cBit_f_TOA[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_s_TOA[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_f_TOT[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_s_TOT[i].set(0x0)
        top.Fpga[0].Asic.SlowControl.cBit_c_TOT[i].set(0x0)

    for i in range(16):
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[i].set(0x0)

    top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(0x40)

    top.Fpga[0].Asic.SlowControl.Write_opt.set(0x0)
    top.Fpga[0].Asic.SlowControl.Precharge_opt.set(0x0)

    top.Fpga[0].Asic.SlowControl.DLL_ALockR_en.set(0x1)
    top.Fpga[0].Asic.SlowControl.CP_b.set(0x5) #5 32ps LSB for B7
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlf_en.set(0x1) #need to fix value externally
    top.Fpga[0].Asic.SlowControl.ext_Vcrtls_en.set(0x1) #need to fix value externally
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlc_en.set(0x1) #0

    top.Fpga[0].Asic.SlowControl.totf_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.totc_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.toa_satovfw.set(0x1)

    top.Fpga[0].Asic.SlowControl.SatFVa.set(0x0) #3
    top.Fpga[0].Asic.SlowControl.IntFVa.set(0x0) #1
    #top.Fpga[0].Asic.SlowControl.SatFTz.set(0x0) #4
    #top.Fpga[0].Asic.SlowControl.IntFTz.set(0x0) #1
    
    top.Fpga[0].Asic.SlowControl.cBitf.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cBits.set(0x0) #f
    top.Fpga[0].Asic.SlowControl.cBitc.set(0x0) #f

    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0x0)  #f
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0x0)  #f
    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cd[0].set(0x7) #6
    top.Fpga[0].Asic.SlowControl.cd[1].set(0x7) #6
    top.Fpga[0].Asic.SlowControl.cd[2].set(0x7) #6
    top.Fpga[0].Asic.SlowControl.dac_biaspa.set(0x1e) #10
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(40) #7
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(320) #173 / 183
    

    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(0x0)   # Rising edge of EXT_TRIG or CMD_PULSE delay
    top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0xfff) # Falling edge of EXT_TRIG (independent of CMD_PULSE)

    top.Fpga[0].Asic.Readout.StartPix.set(pixel_number)
    top.Fpga[0].Asic.Readout.LastPix.set(pixel_number)

#################################################################
def acquire_data(range_low, range_high, range_step, top, 
        asic_pulser, file_prefix, n_iterations, dataStream): 
    
    fileList = []
    useTS = True

    for i in range(range_low, range_high, range_step):
        print(file_prefix+'step = %d' %i)
        asic_pulser.set(i)

        if useTS:
            ts = str(int(time.time()))
            val = '%d_' %i
            filename = 'TestData/'+file_prefix+val+ts+'.dat'
        else:
            filename = 'TestData/'+file_prefix+'%d.dat' %i
            
        try: os.remove(filename)
        except OSError: pass
        
        top.dataWriter._writer.open(filename)
        fileList.append(filename)

        for j in range(n_iterations):
            if (asicVersion == 1):
                top.Fpga[0].Asic.LegacyV1AsicCalPulseStart()
                time.sleep(0.001)
            else:
                top.Fpga[0].Asic.CalPulse.Start()
                time.sleep(0.001)

        while dataStream.count < n_iterations: pass
        top.dataWriter._writer.close()
        dataStream.count = 0

    return fileList
#################################################################
def get_sweep_index(sweep_value, sweep_low, sweep_high, sweep_step):
    if sweep_value < sweep_low or sweep_high < sweep_value:
        raise ValueError( 'Sweep value {} outside of sweep range [{}:{}]'.format(sweep_value, sweep_low, sweep_high) )
    if sweep_value % sweep_step != 0:
        raise ValueError( 'Sweep value {} is not a multiple of sweep step {}'.format(sweep_value, sweep_step) )
    return int ( (sweep_value - sweep_low) / sweep_step )
#################################################################


#################################################################
def toaMeasurement(argip,
    configFile,
    pixel_number,
    Qinj,
    DACvalue,
    DelayRange_low,
    DelayRange_high,
    DelayRange_step):

    asicVersion = 1 # <= Select either V1 or V2 of the ASIC
    DebugPrint = True
    NofIterations = 50  # <= Number of Iterations for each Delay value
    delay_list = range(DelayRange_low,DelayRange_high,DelayRange_step)
    HistDelayTOA1 = 2400  # <= Delay Value for Histogram to be plotted in Plot (1,0)
    HistDelayTOA2 = 2550 # <= Delay Value for Histogram to be plotted in Plot (1,1)
    PlotValidCnt = 1
    
    LSBest = [0]*15
    #add here correct LSBest
    LSBest[4] = 28.64 #ch4

    HistDelayTOA1_index  = get_sweep_index(HistDelayTOA1 , DelayRange_low, DelayRange_high, DelayRange_step)
    HistDelayTOA2_index  = get_sweep_index(HistDelayTOA2 , DelayRange_low, DelayRange_high, DelayRange_step)


    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

#################################################################
    loadDefault = True
    # Setup root class
    if loadDefault:
        top = feb.Top(ip= argip)    
    else:
        top = feb.Top(ip= args.ip, loadYaml= False)    
    print(f'Loading {Configuration_LOAD_file} Configuration File...')
    top.LoadConfig(arg = Configuration_LOAD_file)
    
    if DebugPrint:
        # Tap the streaming data interface (same interface that writes to file)
        dataStream = feb.MyEventReader()    
        pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

    #testing resets
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x0)
    time.sleep(0.001)
    top.Fpga[0].Asic.Gpio.RSTB_TDC.set(0x1)

    # Custom Configuration
    set_fpga_for_custom_config(top)

    fileList = acquire_data(DelayRange_low, DelayRange_high, DelayRange_step, top,
            top.Fpga[0].Asic.Gpio.DlyCalPulseSet, 'TOA', NofIterations, dataStream)

    #######################
    # Data Processing TOA #
    #######################

    Delay = []
    HitCnt = []
    DataMean = []
    DataStdev = []

    for i_del in delay_list:
        delay_value = delay_list[i_del]
        # Create the File reader streaming interface
        dataReader = rogue.utilities.fileio.StreamReader()

        # Create the Event reader streaming interface
        dataStream = feb.MyFileReader()

        # Connect the file reader ---> event reader
        pr.streamConnect(dataReader, dataStream) 

        # Open the file
        dataReader.open(fileList[i_del])

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
    print(DataMean)
    index=np.where(DataMean)
    #avoid crashes due to fit
    #if len(index)>6:
    #    fit = np.polyfit(Delay[index[0][5]:index[0][-5]], DataMean[index[0][5]:index[0][-5]], 1)
    #else: fit=[1,1]

    fit = np.polyfit(Delay[index[0][5]:index[0][-5]], DataMean[index[0][5]:index[0][-5]], 1)
    LSBest = DelayStep/abs(fit[0])

    #################################################################
    # Print Data
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
    # Plot Data

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, figsize=(16,7))

    #LSBest = 1

    # Plot (0,0) ; top left
    #ax1.plot(Delay, np.multiply(DataMean,LSBest))
    ax1.plot(Delay, DataMean)
    ax1.grid(True)
    ax1.set_title('TOA Measurment VS Programmable Delay Value', fontsize = 11)
    ax1.set_xlabel('Programmable Delay Value [step estimate = %f ps]' % DelayStep, fontsize = 10)
    ax1.set_ylabel('Mean Value [ps]', fontsize = 10)
    ax1.legend(['LSB estimate: %f ps' % LSBest],loc = 'upper right', fontsize = 9, markerfirst = False, markerscale = 0, handlelength = 0)
    ax1.set_xlim(left = np.min(Delay), right = np.max(Delay))
    #ax1.set_ylim(bottom = 0, top = np.max(np.multiply(DataMean,LSBest))+100)
    ax1.set_ylim(bottom = 0, top = np.max(DataMean)+100)


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
    toaMeasurement(args.ip,args.cfg,args.ch,args.Q,args.DAC,args.delayMin,args.delayMax,args.delayStep)
