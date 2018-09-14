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
            offset      = 0x00000000, 
            expand      = False,
        ))    

        self.add(common.AltirocProbe(
            name        = 'AltirocProbe', 
            description = 'This device contains Altiroc ASIC\'s probe shift register interface',
            offset      = 0x00010000, 
            expand      = False,
        ))
