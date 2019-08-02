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
#script for irradiation tests
# configure altiroc and launch scope data taking
# example run (delay and probe are optional args):
# python scripts/irrad/probeMeasurement_B1.py --ip 192.168.1.10 --ch 4 --Q 12 --cfg scripts/irrad/config_irrad_B1.yml --DAC 360 
#################################################################
import sys 
import os
import rogue  
import time   
import random 
import argparse
import pyrogue as pr
import pyrogue.gui
import numpy as np
import common as feb
import rogue.utilities.fileio
import statistics 
import math
import matplotlib.pyplot as plt
#################################################################
# Set the argument parser
def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    
    # Add arguments
    parser.add_argument("--ip", nargs = '+', required = True, help = "List of IP addresses")
    parser.add_argument("--cfg", type = str, required = True, help = "config file")
    parser.add_argument("--ch", type = int, required = True, help = "channel")
    parser.add_argument("--Q", type = int, required = True, help = "injected charge DAC")
    parser.add_argument("--DAC", type = int, required = True, help = "DAC vth")
    parser.add_argument("--delay", type = int, required = False, default = 50, help = "DAC delay")
    parser.add_argument("--probePA", type = bool, required = False, default = False, help = "probe PA on")
    parser.add_argument("--runScope", type = bool, required = False, default = False, help = "run scope DAQ")
    
    # Get the arguments
    args = parser.parse_args()
    return args

##################################################################
def setupRogue(argip,configFile):
    # Setup root class
    top = feb.Top(ip= argip)    # Assuming only 1 FPGA

    # Load the default YAML file .... 
    top.LoadConfig(arg='config/defaults.yml')

    # ... then load the User YAML file
    print('Loading Configuration File...')
    top.LoadConfig(arg = configFile)
    
    # Tap the streaming data interface (same interface that writes to file)
    dataStream = feb.LegacyMyEventReader()    
    pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA
    
    return top
    
##################################################################

def probeMeasurement(top,argip,
        configFile,
        pixel_number,
        Qinj, #Pulser Decimal code with added resistance: 3 = 2.66,6 = 5.24, 12 =10.32 fC, 24=20.08 fC  ##
        DACvalue,
        DelayValue=50,
        probePA=False,
        runScope=False):

    NofIterations = 2000  # <= Number of Iterations for each Delay value

    LSBest = 28.64 #ch4
    if pixel_number == 9: 
        LSBest = 30.4
    elif pixel_number == 14: 
        LSBest = 31.28 #ps

    if top == None:
        top = setupRogue(argip,configFile)

    dataStream = feb.LegacyMyEventReader()
    pyrogue.streamTap(top.dataStream[0], dataStream) # Assuming only 1 FPGA

    #################################################################
    # Pixel Readout Selection                                      ##
    #probe configuration
    
    top.Fpga[0].Asic.Probe.en_probe_pa.set(0x0)                        ##
    #top.Fpga[0].Asic.Probe.en_probe_dig.set(0x0)
                                                               ##
    for i in range(25):                                        ##
        top.Fpga[0].Asic.Probe.pix[i].probe_pa.set(0x0)                ## 
        top.Fpga[0].Asic.Probe.pix[i].probe_vthc.set(0x0)              ## 
        top.Fpga[0].Asic.Probe.pix[i].probe_dig_out_disc.set(0x0)      ##
        top.Fpga[0].Asic.Probe.pix[i].probe_toa.set(0x0)               ##
        top.Fpga[0].Asic.Probe.pix[i].probe_tot.set(0x0)               ##
        top.Fpga[0].Asic.Probe.pix[i].totf.set(0x0)                    ##
        top.Fpga[0].Asic.Probe.pix[i].tot_overflow.set(0x0)            ##
        top.Fpga[0].Asic.Probe.pix[i].toa_busy.set(0x0)                ##
        top.Fpga[0].Asic.Probe.pix[i].Hit.set(0x0)               ## digital_probe2 (was toa_ready in Legacy V1)
        top.Fpga[0].Asic.Probe.pix[i].tot_busy.set(0x0)                ##
        top.Fpga[0].Asic.Probe.pix[i].tot_ready.set(0x0)               ##
        top.Fpga[0].Asic.Probe.pix[i].en_read.set(0x0)                 ##
    
                                                           ##
    if pixel_number in range(0, 5):                            ##
        if probePA: top.Fpga[0].Asic.Probe.en_probe_pa.set(0x1)                        ##
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x1)                   ## 0x1
        top.Fpga[0].Asic.Probe.EN_dout.set(0x1)                        ##
    if pixel_number in range(5, 10):                           ##
        if probePA: top.Fpga[0].Asic.Probe.en_probe_pa.set(0x2)                        ##
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x2)                   ## 0x2
        top.Fpga[0].Asic.Probe.EN_dout.set(0x2)                        ##
    if pixel_number in range(10, 15):                          ##
        if probePA: top.Fpga[0].Asic.Probe.en_probe_pa.set(0x4)                        ##
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x4)                   ## 0x4
        top.Fpga[0].Asic.Probe.EN_dout.set(0x4)                        ##
    if pixel_number in range(15, 20):                          ##
        if probePA: top.Fpga[0].Asic.Probe.en_probe_pa.set(0x8)                        ##
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x8)                   ## 0x8
        top.Fpga[0].Asic.Probe.EN_dout.set(0x8)                        ##
    if pixel_number in range(20, 25):                          ##
        if probePA: top.Fpga[0].Asic.Probe.en_probe_pa.set(0x10)                        ##
        top.Fpga[0].Asic.Probe.en_probe_dig.set(0x10)                  ##
        top.Fpga[0].Asic.Probe.EN_dout.set(0x10)                       ##

    
    if probePA: top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x1)         ## 
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_vthc.set(0x1)       ## 
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x1)#
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_toa.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_tot.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].totf.set(0x0)             ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_overflow.set(0x0)     ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].toa_busy.set(0x0)         ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].Hit.set(0x0)               ## digital_probe2 (was toa_ready in Legacy V1)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_busy.set(0x0)         ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_ready.set(0x0)        ##
    top.Fpga[0].Asic.Probe.pix[pixel_number].en_read.set(0x1)          ##
    #################################################################
    
    #################################################################
    # Custom Configuration                                         ##
                                                                   ##
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
                                                               ##
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf) #f  ##
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0) #0  ##
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf) #0  ##
                                                               ##
    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(0x0) #0                   ##
    top.Fpga[0].Asic.SlowControl.Cp_Vpa.set(0x0) #0                    ##
    top.Fpga[0].Asic.SlowControl.cd[0].set(0x7) # ch4 - Cd = 0.5*n
    top.Fpga[0].Asic.SlowControl.cd[1].set(0x7) # ch9
    top.Fpga[0].Asic.SlowControl.cd[2].set(0x7) # ch14
    top.Fpga[0].Asic.SlowControl.dac_biaspa.set(30) #10 30= 0x1e 60=0x3c ##
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(Qinj) # Modified Pulser Decimal code 3 = 2.66,6 = 5.24, 12 =10.32 fC, 24=20.08 fC  ##
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(DACvalue)           ##
    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(0) # Rising edge of EXT_TRIG
    top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(DelayValue) # Falling edge of EXT_TRIG
    
    #################################################################
    time.sleep(0.5)
    print('Done configuring ASIC ---')
    # Take data with scope
    files = []
    if runScope:
      if not os.path.isdir('./Data'):
          os.mkdir('Data')
      from subprocess import call
      call('./lecroy_example',shell=True)
      #find new files (should be 2) and move to correct folder
      files = os.listdir('Data/')
      for filename in files:
        oldName = './Data/'+filename
        newName = '/home/hgtd-lal/Documents/ALTIROC1/IrradMeasurements/oscilloscope/ch'+str(pixel_number)+'/'+filename
        os.rename(oldName,newName)

    #################################################################
    
    time.sleep(0.5)
    # Close
    top.stop()
    
    return files
#################################################################
#################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)
    probeMeasurement(None,args.ip,args.cfg,args.ch,args.Q,args.DAC,args.delay,args.probePA,args.runScope)