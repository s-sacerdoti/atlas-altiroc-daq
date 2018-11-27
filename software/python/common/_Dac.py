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

        self.add(pr.LinkVariable(
            name         = 'FloatValue', 
            mode         = 'RW', 
            units        = 'V',
            disp         = '{:1.3f}',
            linkedGet    = self.getVoltage,
            linkedSet    = self.setVoltage,
            dependencies = [self.variables['RawValue']],
        ))         

    @staticmethod
    def getVoltage(var):
        value = var.dependencies[0].value()
        return (value/2**16)*(1.024)

    @staticmethod
    def setVoltage(var, value, write):
        # Check for a non-negative value
        if (value>=0) and (value<1.024):
            # Calculate the RAW value
            newValue = (value/1.024)*(2**16)
            # Update the register
            var.dependencies[0].set(int(newValue),write)
        else:
            print( 'Fpga.Dac.setVoltage(): %f must be > 0V and < 1.024V' % value )        
        