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

class AltirocGpio(pr.Device):
    def __init__(   
        self,       
        name        = 'AltirocGpio',
        description = 'Container for Altiroc ASIC\'s GPIOs',
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        self.add(pr.RemoteVariable(
            name         = 'RSTB_RAM', 
            description  = 'reset input active LOW',
            offset       = 0x00,
            bitSize      = 1, 
            mode         = 'RW',
            units        = 'active LOW',            
        )) 
            
        self.add(pr.RemoteVariable(
            name         = 'RST_COUNTER', 
            description  = 'reset input active HIGH',
            offset       = 0x04,
            bitSize      = 1, 
            mode         = 'RW',
            units        = 'active HIGH',            
        ))             

        self.add(pr.RemoteVariable(
            name         = 'RSTB_TDC', 
            description  = 'reset input active LOW',
            offset       = 0x08,
            bitSize      = 1, 
            mode         = 'RW',
            units        = 'active LOW',            
        ))     

        self.add(pr.RemoteVariable(
            name         = 'RSTB_DLL', 
            description  = 'reset input active LOW',
            offset       = 0x0C,
            bitSize      = 1, 
            mode         = 'RW',
            units        = 'active LOW',            
        ))  

        self.add(pr.RemoteVariable(
            name         = 'DIGITAL_PROBE', 
            description  = 'reset input active LOW',
            offset       = 0x10,
            bitSize      = 2, 
            mode         = 'RO',
            pollInterval = 1,
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'DlyCalPulseSet', 
            description  = 'Sets the delay of CMD_PULSE_P pulse and EXT_TRIG rising edge delay. Delay will be linear [0x000:0xBFF] then saturate to 0xBFF for [0xC00:0xFFF]',
            offset       = 0x14,
            bitSize      = 12, 
            mode         = 'RW',
            units        = '10ps',
            disp         = '{:d}',
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'DlyCalPulseReset', 
            description  = 'Sets the delay of EXT_TRIG falling edge delay. Delay will be linear [0x000:0xBFF] then saturate to 0xBFF for [0xC00:0xFFF]',
            offset       = 0x18,
            bitSize      = 12, 
            mode         = 'RW',
            units        = '10ps',
            disp         = '{:d}',
        ))        
        
        # self.add(pr.RemoteVariable(
            # name         = 'RefClkSel', 
            # description  = 'Reference Clock Select: Si5345.IN_SEL_REGCTRL must be 0x0 for CLKIN controlled by this else Si5345.IN_SEL controls the CLKIN MUXing',
            # offset       = 0x1C,
            # bitSize      = 2, 
            # mode         = 'RW',
            # enum         = {
                # 0x0: 'IntClk', 
                # 0x1: 'ExtSmaClk', 
                # 0x2: 'ExtLemoClk',
            # },
        # ))        
