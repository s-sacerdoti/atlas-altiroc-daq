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

class Altiroc(pr.Device):
    def __init__(   
        self,       
        name        = "Altiroc",
        description = "Container for Altiroc ASIC",
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        self.add(common.AltirocSlowControl(
            name        = 'AltirocSlowControl', 
            description = 'This device contains Altiroc ASIC\'s slow control shift register interface',
            offset      = 0x00010000, 
            expand      = False,
        ))    

        self.add(common.AltirocProbe(
            name        = 'AltirocProbe', 
            description = 'This device contains Altiroc ASIC\'s probe shift register interface',
            offset      = 0x00020000, 
            expand      = False,
        ))

        self.add(pr.RemoteVariable(
            name         = 'RENABLE', 
            description  = 'Read (SRAM) Enable',
            offset       = 0x800,
            bitSize      = 1, 
            mode         = 'RW',
        ))

        self.add(pr.RemoteVariable(
            name         = 'RSTB_RAM', 
            description  = 'reset input active LOW',
            offset       = 0x804,
            bitSize      = 1, 
            mode         = 'RW',
        )) 

        self.add(pr.RemoteVariable(
            name         = 'RSTB_READ', 
            description  = 'reset input active LOW',
            offset       = 0x808,
            bitSize      = 1, 
            mode         = 'RW',
        ))

        self.add(pr.RemoteVariable(
            name         = 'RSTB_TDC', 
            description  = 'reset input active LOW',
            offset       = 0x80C,
            bitSize      = 1, 
            mode         = 'RW',
        )) 

        self.add(pr.RemoteVariable(
            name         = 'RSTB_COUNTER', 
            description  = 'reset input active LOW',
            offset       = 0x810,
            bitSize      = 1, 
            mode         = 'RW',
        ))

        self.add(pr.RemoteVariable(
            name         = 'CK_WRITE', 
            description  = 'External ck used to write data in the SRAM instead of the internal one (to write slower for instance)',
            offset       = 0x814,
            bitSize      = 1, 
            mode         = 'RW',
            enum        = {
                0x0: 'Disabled', 
                0x1: '80MHz', 
                0x2: '40MHz', 
                0x3: '20MHz', 
                0x4: '10MHz', 
                0x5: '5MHz', 
                0x6: '2.5MHz', 
                0x7: '1.25MHz',                 
            },
        ))        
        