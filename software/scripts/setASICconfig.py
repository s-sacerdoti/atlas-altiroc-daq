def set_pixel_specific_parameters(top, pixel_number):
    if pixel_number in range(0, 5): bitset=0x1
    if pixel_number in range(5, 10): bitset=0x2
    if pixel_number in range(10, 15): bitset=0x4
    if pixel_number in range(15, 20): bitset=0x8
    if pixel_number in range(20, 25): bitset=0x10

    top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(0x40)
    top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_trig_ext[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf)
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf)

    top.Fpga[0].Asic.Probe.EN_dout.set(bitset)
    top.Fpga[0].Asic.Probe.en_probe_pa.set(bitset)
    top.Fpga[0].Asic.Probe.en_probe_dig.set(bitset)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x1)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_vthc.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x1)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_toa.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_tot.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].totf.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_overflow.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].toa_busy.set(0x1)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_busy.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_ready.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].en_read.set(0x1)
    top.Fpga[0].Asic.Probe.pix[pixel_number].toa_busy.set(0x0)

    top.Fpga[0].Asic.Readout.StartPix.set(pixel_number)
    top.Fpga[0].Asic.Readout.LastPix.set(pixel_number)
