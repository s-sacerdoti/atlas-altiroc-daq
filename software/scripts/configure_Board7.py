def getBoardConfig():
    
    board_config = {}
    
    board_config['Rin_Vpa']      = 0x0
    board_config['cd'] = [0x7,0x7,0x7,0x7,0x7]
    board_config['dac_biaspa'] = 0x1e
    board_config['dac_pulser'] = 13
    board_config['DAC10bit'] = 320

    board_config['CP_b'] = 0x5
    board_config['ext_Vcrtlf_en'] = 0x1
    board_config['ext_Vcrtls_en'] = 0x1
    board_config['ext_Vcrtlc_en'] = 0x1
    board_config['DLL_ALockR_en'] = 0x1
    board_config['totf_satovfw'] = 0x1
    board_config['totc_satovfw'] = 0x1
    board_config['toa_satovfw'] = 0x1
    board_config['SatFVa'] = 0x0
    board_config['IntFVa'] = 0x0
    board_config['cBitf'] = 0x0
    board_config['cBits'] = 0x0
    board_config['cBitc'] = 0x0

    #pixel config (all 0 for the moment)
    board_config['cBit_f_TOA'] = [0]*15
    board_config['cBit_s_TOA'] = [0]*15
    board_config['cBit_f_TOT'] = [0]*15
    board_config['cBit_s_TOT'] = [0]*15
    board_config['cBit_c_TOT'] = [0]*15
    
    return board_config
