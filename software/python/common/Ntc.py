#!/usr/bin/env python3
##############################################################################
## This file is part of 'ATLAS RD53 DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS RD53 DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

import pyrogue as pr

class Ntc(pr.Device):
    def __init__(   
        self,       
        name        = "Ntc",
        description = "Container for MAX6682 SPI modules",
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        for i in range(4):

            self.add(pr.RemoteVariable(  
                name        = ('Dout[%d]' % i),
                description = 'Max6682 Data output',
                offset      = (4*i), 
                bitSize     = 11,  
                base        = pr.UInt,
                mode        = 'RO',
                pollInterval = 5,
            )) 

            # self.add(pr.LinkVariable(
                # name         = ('Temp[%d]' % i), 
                # mode         = 'RO', 
                # units        = 'degC',
                # linkedGet    = self.convTemp,
                # disp         = '{:1.3f}',
                # dependencies = [self.variables[('Dout[%d]' % i)]],
            # ))            
        
    # @staticmethod
    # def convTemp(dev, var):
        # ##########################################################################
        # # Based on 6th order polynomial fit of Table 1
        # # y = -2E-13x6 + 2E-09x5 - 5E-06x4 + 0.0082x3 - 7.448x2 + 3606.4x - 723443
        # ##########################################################################
        # x  = var.dependencies[0].value()
        # x ^= 0x400 # Convert to binary with offset
        # x  = float(x)        
        # return (-2.0E-13*(x**6) + 2.0E-09*(x**5) - 5.0E-06*(x**4) + 0.0082*(x**3) - 7.448*(x**2) + 3606.4*(x**1) - 723443.0*(x**0))
