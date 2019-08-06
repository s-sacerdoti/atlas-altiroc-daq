#!/usr/bin/env python3
#################################################################
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

##############################################################################
def set_fpga_for_custom_config(top,pixel_number):
    print('Loading custom config for BOARD 6')
    top.Fpga[0].Asic.Probe.en_probe_pa.set(0x1)

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
    top.Fpga[0].Asic.SlowControl.CP_b.set(0x0) #5
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlf_en.set(0x1) #need to fix value externally
    top.Fpga[0].Asic.SlowControl.ext_Vcrtls_en.set(0x1) #need to fix value externally
    top.Fpga[0].Asic.SlowControl.ext_Vcrtlc_en.set(0x0) #0

    top.Fpga[0].Asic.SlowControl.totf_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.totc_satovfw.set(0x1)
    top.Fpga[0].Asic.SlowControl.toa_satovfw.set(0x1)

    top.Fpga[0].Asic.SlowControl.SatFVa.set(0x4) #3
    top.Fpga[0].Asic.SlowControl.IntFVa.set(0x0) #1
    #top.Fpga[0].Asic.SlowControl.SatFTz.set(0x0) #4
    #top.Fpga[0].Asic.SlowControl.IntFTz.set(0x0) #1
    
    top.Fpga[0].Asic.SlowControl.cBitf.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cBits.set(0x0) #f
    top.Fpga[0].Asic.SlowControl.cBitc.set(0x0) #f

    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf)  #f
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0)  #0
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf)  #f
    top.Fpga[0].Asic.SlowControl.Rin_Vpa.set(0x0) #0
    top.Fpga[0].Asic.SlowControl.cd[0].set(0x7) #6
    top.Fpga[0].Asic.SlowControl.cd[1].set(0x7) #6
    top.Fpga[0].Asic.SlowControl.cd[2].set(0x7) #6
    top.Fpga[0].Asic.SlowControl.dac_biaspa.set(0x1e) #10
    top.Fpga[0].Asic.SlowControl.dac_pulser.set(12) #7
    top.Fpga[0].Asic.SlowControl.DAC10bit.set(320) #173 / 183
    
    #top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x0)
    #time.sleep(0.001)
    #top.Fpga[0].Asic.Gpio.RSTB_DLL.set(0x1)

    top.Fpga[0].Asic.Gpio.DlyCalPulseSet.set(0x0)   # Rising edge of EXT_TRIG or CMD_PULSE delay
    top.Fpga[0].Asic.Gpio.DlyCalPulseReset.set(0xfff) # Falling edge of EXT_TRIG (independent of CMD_PULSE)

    top.Fpga[0].Asic.Readout.StartPix.set(pixel_number)
    top.Fpga[0].Asic.Readout.LastPix.set(pixel_number)
