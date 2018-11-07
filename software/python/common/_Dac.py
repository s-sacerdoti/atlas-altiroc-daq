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

class Dac(pr.Device):
    def __init__(   
        self,       
        name        = "Dac",
        description = "Container for AD5662 SPI modules",
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        self.add(pr.RemoteVariable(
            name        = 'RawValue',
            description = '16-bit DAC Value',
            offset      = 0x0,
            bitSize     = 16,
            mode        = 'WO',
            units        = '1.024V/2^16',
        ))   
