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
            name        = 'Value',
            description = '16-bit DAC Value',
            offset      = 0x0,
            bitSize     = 16,
            mode        = 'WO',
        ))   

        self.add(pr.LinkVariable(
            name         = 'Voltage', 
            mode         = 'RO', 
            units        = 'V',
            linkedGet    = self.convVolts,
            disp         = '{:1.3f}',
            dependencies = [self.variables['Value']],
        ))         
                    
    @staticmethod
    def convVolts(dev, var):
        x  = var.dependencies[0].value() 
        return ((1.024*float(x))/65536.0)
