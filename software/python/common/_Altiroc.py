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
import time

class Altiroc(pr.Device):
    def __init__(   
        self,       
        name        = 'Altiroc',
        description = 'Container for Altiroc ASIC',
        asyncDev    = None,
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)

        self.add(common.AltirocGpio(
            name        = 'Gpio', 
            description = 'This device contains Altiroc ASIC\'s ASYNC GPIO interfaces',
            offset      = 0x00000000, 
            expand      = False,
        )) 
        
        self.add(common.AltirocTdcClk(
            name        = 'TdcClk', 
            description = 'This device contains Altiroc ASIC\'s TDC Clock configurations',
            offset      = 0x00010000, 
            enableDeps  = asyncDev,
            expand      = False,
        ))          
        
        self.add(common.AltirocCalPulse(
            name        = 'CalPulse', 
            description = 'This device contains Altiroc ASIC\'s cal pulse controls',
            offset      = 0x00020000, 
            enableDeps  = asyncDev,
            expand      = False,
        ))      

        self.add(common.AltirocTrig(
            name        = 'Trig', 
            description = 'This device contains Altiroc ASIC\'s triggering controls',
            offset      = 0x00030000, 
            enableDeps  = asyncDev,
            expand      = False,
        ))              
        
        self.add(common.AltirocSlowControl(
            name        = 'SlowControl', 
            description = 'This device contains Altiroc ASIC\'s slow control shift register interface',
            offset      = 0x00040000, 
            expand      = False,
        ))    

        self.add(common.AltirocProbe(
            name        = 'Probe', 
            description = 'This device contains Altiroc ASIC\'s probe shift register interface',
            offset      = 0x00050000, 
            enableDeps  = asyncDev,
            expand      = False,
        ))
        
        self.add(common.AltirocReadout(
            name        = 'Readout', 
            description = 'This device contains Altiroc ASIC\'s readout controls',
            offset      = 0x00060000, 
            enableDeps  = asyncDev,
            expand      = False,
        ))          

        @self.command()
        def LegacyV1AsicCalPulseStart():
        
            # Resets
            self.Gpio.RSTB_RAM.set(0x0)
            self.Gpio.RSTB_TDC.set(0x0)
            
            # Clears
            self.Gpio.RSTB_RAM.set(0x1)                
            self.Gpio.RSTB_TDC.set(0x1) 
            
            # Start the Cal pulse
            self.CalPulse.Start()
