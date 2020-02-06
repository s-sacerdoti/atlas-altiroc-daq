def set_pixel_specific_parameters(top, pixel_number):

    readAllData=False
        
    #Ctest,discri,PA,SRAM off for all channels
    for ipix in range(25):
        top.Fpga[0].Asic.SlowControl.disable_pa[ipix].set(0x1)	
        top.Fpga[0].Asic.SlowControl.ON_discri[ipix].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[ipix].set(0x0)#New
        top.Fpga[0].Asic.SlowControl.ON_Ctest[ipix].set(0x0)
        top.Fpga[0].Asic.SlowControl.EN_trig_ext[ipix].set(0x0)

    #B13 6dead 7prb et 13prb
    #for ipix in range(15):
    #for ipix in list(range(0,6))+list(range(7,15)):
    #for ipix in [0,1,2,3,4,5,9,10,11,12,14]:#Why 8 remove?
    #for ipix in [3,4,5,9,10,11,12,14]:
    #for ipix in range(0,5):
    for ipix in [1,2]:
        #top.Fpga[0].Asic.SlowControl.disable_pa[ipix].set(0x0)	
        #top.Fpga[0].Asic.SlowControl.ON_discri[ipix].set(0x1)
        #top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[ipix].set(0x1)#New
        #top.Fpga[0].Asic.SlowControl.ON_Ctest[ipix].set(0x1)
        #top.Fpga[0].Asic.SlowControl.EN_trig_ext[ipix].set(0x1)
        pass
    #top.Fpga[0].Asic.SlowControl.ON_Ctest[2].set(0x0)
    
    #turn on only one channel
    top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.ON_Ctest[pixel_number].set(0x1)


    #Other slow control parameters
    #top.Fpga[0].Asic.SlowControl.bit_vth_cor[pixel_number].set(0x40)
    top.Fpga[0].Asic.SlowControl.EN_hyst[pixel_number].set(0x1)
    top.Fpga[0].Asic.SlowControl.cBit_f_TOA[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_s_TOA[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_f_TOT[pixel_number].set(0xf)
    top.Fpga[0].Asic.SlowControl.cBit_s_TOT[pixel_number].set(0x0)
    top.Fpga[0].Asic.SlowControl.cBit_c_TOT[pixel_number].set(0xf)



    #find columns
    if pixel_number in range(0, 5): bitset=0x1
    if pixel_number in range(5, 10): bitset=0x2
    if pixel_number in range(10, 15): bitset=0x4
    if pixel_number in range(15, 20): bitset=0x8
    if pixel_number in range(20, 25): bitset=0x10
    
    #Probes off
    top.Fpga[0].Asic.Probe.EN_dout.set(bitset)
    top.Fpga[0].Asic.Probe.en_probe_pa.set(bitset) # was bitset
    top.Fpga[0].Asic.Probe.en_probe_dig.set(bitset) # was bitset
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_pa.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_vthc.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_dig_out_disc.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_toa.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].probe_tot.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].totf.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_overflow.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].toa_busy.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_busy.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].tot_ready.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].toa_busy.set(0x0)
    top.Fpga[0].Asic.Probe.pix[pixel_number].en_read.set(0x1)

    #Readout
    top.Fpga[0].Asic.Readout.ReadoutSize.set(0)
    top.Fpga[0].Asic.Readout.RdIndexLut[0].set(pixel_number)



    if readAllData:
        N=15
        #chList=[pixel_number]+[x for x in range(N) if x != pixel_number]
        chList=range(N)
        print (chList,len(chList))
        top.Fpga[0].Asic.Readout.ReadoutSize.set(len(chList)-1)
        for ipix,pix in enumerate(chList):
            top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[ipix].set(0x1)
            top.Fpga[0].Asic.Readout.RdIndexLut[ipix].set(pix)
