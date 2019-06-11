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

class AltirocTdcClk(pr.Device):
    def __init__(   
        self,       
        name        = 'AltirocTdcClk',
        description = 'Container for Altiroc ASIC\'s TDC CLK configuration',
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
                    
        self.add(pr.RemoteVariable(
            name         = 'Tdc40MHzClkSel', 
            description  = 'Select the 40 MHz used by ASIC TDC: 0 = Si5345 ouput, 1 = FPGA output',
            offset       = 0x0,
            bitSize      = 1, 
            mode         = 'RW',
            enum         = {
                0x0: 'Pll', 
                0x1: 'Fpga', 
            },
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'FpgaTdcClkHigh', 
            description  = 'FPGA TDC Clock high phase width (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x4,
            bitSize      = 8, 
            mode         = 'RW',
        ))  
        
        self.add(pr.RemoteVariable(
            name         = 'FpgaTdcClkLow', 
            description  = 'FPGA TDC Clock low phase width (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x8,
            bitSize      = 8, 
            mode         = 'RW',
        ))          
        
        self.add(pr.LinkVariable(
            name         = 'FpgaTdcClkHighNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.FpgaTdcClkHigh],
            linkedGet    = common.getNsValue,
        ))    
        
        self.add(pr.LinkVariable(
            name         = 'FpgaTdcClkLowNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.FpgaTdcClkLow],
            linkedGet    = common.getNsValue,
        ))  
        
        self.add(pr.LinkVariable(
            name         = 'FpgaTdcClkFreq', 
            units        = 'MHz',
            disp         = '{:1.2f}',
            dependencies = [self.FpgaTdcClkHigh,self.FpgaTdcClkLow],
            linkedGet    = common.getMhzValue,
        )) 
        