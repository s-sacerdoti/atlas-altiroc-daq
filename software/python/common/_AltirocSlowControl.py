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

import pyrogue as pr
import common 

class AltirocSlowControl(pr.Device):
    def __init__(   
        self,       
        name        = "AltirocSlowControl",
        description = "Container for Altiroc ASIC's slow control shift register",
            **kwargs):
        
        super().__init__(name=name,description=description,**kwargs)
        
        downToBitOrdering = pr.UIntReversed 
        upToBitOrdering   = pr.UInt  
        
        def addReg(name,description,bitSize,bitOffset,value,base):
            
            remap = divmod((bitOffset-1),32)
        
            self.add(pr.RemoteVariable(  
                name        = name, 
                description = description,
                base        = base,
                offset      = (remap[0]<<2),
                mode        = 'RW', 
                bitSize     = bitSize, 
                bitOffset   = remap[1],
                # value       = value, 
            ))
        
        addReg(
            name        = 'dac', 
            description = 'ALTLAS LARG DAC',
            bitSize     = 10, 
            bitOffset   = 1,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )

        addReg(
            name        = 'ON_dac_LR', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 11,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,
        )        
          
        ##############
        # bias_channel
        ##############
        
        addReg(
            name        = 'Write_opt', 
            description = 'SRAM',
            bitSize     = 1, 
            bitOffset   = 12,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )  

        addReg(
            name        = 'Precharge_opt', 
            description = 'SRAM',
            bitSize     = 1, 
            bitOffset   = 13,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )   

        addReg(
            name        = 'ref_bg', 
            description = 'Bandgap',
            bitSize     = 1, 
            bitOffset   = 14,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,
        )   

        addReg(
            name        = 'dac_pulser', 
            description = 'Internal pulser',
            bitSize     = 6, 
            bitOffset   = 15,
            value       = 0x7, # DEF Value
            base        = downToBitOrdering,
        ) 

        addReg(
            name        = 'Ccomp_TZ', 
            description = 'for TZ preamp only',
            bitSize     = 1, 
            bitOffset   = 21,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        ) 

        addReg(
            name        = 'Rin_Vpa', 
            description = 'DEF=25K Vpa only',
            bitSize     = 1, 
            bitOffset   = 22,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )     

        addReg(
            name        = 'Cp_Vpa', 
            description = 'Cpole VPA preamp',
            bitSize     = 3, 
            bitOffset   = 23,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        ) 

        addReg(
            name        = 'dac_biaspa', 
            description = 'Id input trans',
            bitSize     = 6, 
            bitOffset   = 26,
            value       = 0xC, # DEF Value
            base        = downToBitOrdering,
        )  

        addReg(
            name        = 'ON_dac_biaspa', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 32,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,
        )  

        addReg(
            name        = 'ON_ota_dac', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 33,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,
        )    

        addReg(
            name        = 'DAC10bit', 
            description = '10 bit DAC to set Vth (Treshold)',
            bitSize     = 10, 
            bitOffset   = 34,
            value       = 0x80, # DEF Value
            base        = downToBitOrdering,
        )

        addReg(
            name        = 'SatFVa', 
            description = 'TDC VPA',
            bitSize     = 3, 
            bitOffset   = 44,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )   

        addReg(
            name        = 'IntFVa', 
            description = '',
            bitSize     = 3, 
            bitOffset   = 47,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )  

        addReg(
            name        = 'SatFTz', 
            description = 'TDC TZ',
            bitSize     = 3, 
            bitOffset   = 50,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        ) 

        addReg(
            name        = 'IntFTz', 
            description = '',
            bitSize     = 3, 
            bitOffset   = 53,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )   

        addReg(
            name        = 'totf_satovfw', 
            description = 'TOT fine',
            bitSize     = 1, 
            bitOffset   = 56,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )   

        addReg(
            name        = 'totc_satovfw', 
            description = 'TOT coarse',
            bitSize     = 1, 
            bitOffset   = 57,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )
        
        addReg(
            name        = 'toa_satovfw', 
            description = 'TOA overflow',
            bitSize     = 1, 
            bitOffset   = 58,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )
        
        addReg(
            name        = 'ckw_choice', 
            description = 'DLL',
            bitSize     = 1, 
            bitOffset   = 59,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )  
        
        addReg(
            name        = 'cBitf', 
            description = '',
            bitSize     = 4, 
            bitOffset   = 60,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,
        )  

        addReg(
            name        = 'DLL_ALockR_en', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 64,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,
        ) 

        addReg(
            name        = 'CP_b', 
            description = '',
            bitSize     = 3, 
            bitOffset   = 65,
            value       = 0x3, # DEF Value
            base        = upToBitOrdering,
        )         
        
        addReg(
            name        = 'ext_Vcrtlf_en', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 68,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )

        addReg(
            name        = 'cBits', 
            description = '',
            bitSize     = 4, 
            bitOffset   = 69,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,
        )

        addReg(
            name        = 'ext_Vcrtls_en', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 73,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )    

        addReg(
            name        = 'cBitc', 
            description = '',
            bitSize     = 4, 
            bitOffset   = 74,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,
        ) 

        addReg(
            name        = 'ext_Vcrtlc_en', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 78,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )

        addReg(
            name        = 'en_8drivers', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 79,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,
        )        

        ######################
        # Pixel Configurations
        ######################
        
        pixChBitOffset = [80,113,146,179,215,248,281,314,347,383,416,449,482,515,551,584,617,650,683,719,752,785,818,851,887]
        
        for i in range(25):
        
            addReg(
                name        = ('EN_ck_SRAM[%d]' % i), 
                description = '',
                bitSize     = 1, 
                bitOffset   = (0+pixChBitOffset[i]),
                value       = 0x1, # DEF Value
                base        = downToBitOrdering,
            )

            addReg(
                name        = ('ON_Ctest[%d]' % i), 
                description = '',
                bitSize     = 1, 
                bitOffset   = (1+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            ) 

            addReg(
                name        = ('disable_pa[%d]' % i), 
                description = '',
                bitSize     = 1, 
                bitOffset   = (2+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            ) 

            addReg(
                name        = ('bit_vth_cor[%d]' % i), 
                description = '',
                bitSize     = 7, 
                bitOffset   = (3+pixChBitOffset[i]),
                value       = 0x8, # DEF Value
                base        = downToBitOrdering,
            )         
            
            addReg(
                name        = ('ON_discri[%d]' % i), 
                description = '',
                bitSize     = 1, 
                bitOffset   = (10+pixChBitOffset[i]),
                value       = 0x1, # DEF Value
                base        = downToBitOrdering,
            )  

            addReg(
                name        = ('EN_hyst[%d]' % i), 
                description = '',
                bitSize     = 1, 
                bitOffset   = (11+pixChBitOffset[i]),
                value       = 0x1, # DEF Value
                base        = downToBitOrdering,
            )    

            addReg(
                name        = ('EN_trig_ext[%d]' % i), 
                description = '',
                bitSize     = 1, 
                bitOffset   = (12+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            )  
            
            addReg(
                name        = ('cBit_f_TOT[%d]' % i), 
                description = '',
                bitSize     = 4, 
                bitOffset   = (13+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            )  

            addReg(
                name        = ('cBit_c_TOT[%d]' % i), 
                description = '',
                bitSize     = 4, 
                bitOffset   = (17+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            )   

            addReg(
                name        = ('cBit_s_TOT[%d]' % i), 
                description = '',
                bitSize     = 4, 
                bitOffset   = (21+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            )

            addReg(
                name        = ('cBit_s_TOA[%d]' % i), 
                description = '',
                bitSize     = 4, 
                bitOffset   = (25+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            )  

            addReg(
                name        = ('cBit_f_TOA[%d]' % i), 
                description = '',
                bitSize     = 4, 
                bitOffset   = (29+pixChBitOffset[i]),
                value       = 0x0, # DEF Value
                base        = downToBitOrdering,
            )              
        
            cdBitOffset = [212,380,548,716,884]
            
        for i in range(5):        
    
            addReg(
                name        = ('cd[%d]' % i), 
                description = 'In units of 0.5pF',
                bitSize     = 3, 
                bitOffset   = cdBitOffset[i],
                value       = 0x0, # DEF Value
                base        = upToBitOrdering,
            )          
            
        ###############
        # Phase shifter
        ###############
        
        addReg(
            name        = 'PLL', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 920,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,            
        ) 

        addReg(
            name        = 'dac_icpb', 
            description = '',
            bitSize     = 6, 
            bitOffset   = 921,
            value       = 0xA, # DEF Value
            base        = upToBitOrdering,            
        ) 

        addReg(
            name        = 'dac_CP_BWb', 
            description = '',
            bitSize     = 6, 
            bitOffset   = 927,
            value       = 0x20, # DEF Value
            base        = upToBitOrdering,            
        )

        addReg(
            name        = 'EN_Ext_Vin_VCO',
            description = '',
            bitSize     = 1, 
            bitOffset   = 933,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,            
        )

        addReg(
            name        = 'setN', 
            description = '',
            bitSize     = 2, 
            bitOffset   = 934,
            value       = 0x3, # DEF Value
            base        = upToBitOrdering,            
        )

        addReg(
            name        = 'setProbe', 
            description = '',
            bitSize     = 3, 
            bitOffset   = 936,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,            
        )  

        addReg(
            name        = 'EN_500', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 939,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,            
        )

        addReg(
            name        = 'EN_1000', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 940,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,            
        ) 

        addReg(
            name        = 'EN_2000', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 941,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,            
        ) 

        addReg(
            name        = 'EN_4000', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 942,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,            
        )  

        addReg(
            name        = 'EN_200p', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 943,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,            
        ) 

        addReg(
            name        = 'EN_LowKvco', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 944,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,            
        )         
        
        ####################        
        # 640M_Phase shifter
        ####################  

        addReg(
            name        = 'delay', 
            description = '',
            bitSize     = 8, 
            bitOffset   = 945,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,              
        ) 

        addReg(
            name        = 'Ph', 
            description = 'Change internal clock from PLL or external input',
            bitSize     = 2, 
            bitOffset   = 953,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,              
        ) 

        addReg(
            name        = 'forcedown', 
            description = 'DLL force down',
            bitSize     = 1, 
            bitOffset   = 955,
            value       = 0x0, # DEF Value
            base        = downToBitOrdering,             
        )

        addReg(
            name        = 'inita', 
            description = 'Initial Vbias',
            bitSize     = 1, 
            bitOffset   = 956,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,             
        ) 

        addReg(
            name        = 'initb', 
            description = 'Initial Vbias',
            bitSize     = 1, 
            bitOffset   = 957,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,             
        ) 

        addReg(
            name        = 'initc', 
            description = 'Initial Vbias',
            bitSize     = 1, 
            bitOffset   = 958,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,             
        )

        addReg(
            name        = 'cpen', 
            description = 'Charge pump bias enable',
            bitSize     = 1, 
            bitOffset   = 959,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,             
        )

        addReg(
            name        = 'cp', 
            description = 'charge pump current adjust.',
            bitSize     = 4, 
            bitOffset   = 960,
            value       = 0x0, # DEF Value
            base        = upToBitOrdering,             
        ) 

        addReg(
            name        = 'En_40M', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 964,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,             
        )

        addReg(
            name        = 'En_640M', 
            description = '',
            bitSize     = 1, 
            bitOffset   = 965,
            value       = 0x1, # DEF Value
            base        = downToBitOrdering,             
        )        
        
        self.add(pr.RemoteVariable(
            name         = 'rstL', 
            description  = 'Shift Register\'s reset (active LOW)',
            offset       = 0xFFC,
            bitSize      = 1, 
            mode         = 'RW',
            base         = pr.UInt,
            value       = 0x1,
        ))         
        
