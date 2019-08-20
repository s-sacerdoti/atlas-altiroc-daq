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

class AltirocCalPulse(pr.Device):
    def __init__(   
        self,       
        name        = 'AltirocCalPulse',
        description = 'Container for Altiroc ASIC\'s calibration pulse registers',
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        self.add(pr.RemoteVariable(
            name         = 'CalPulseDelay', 
            description  = 'delay between cal pulses (zero inclusive)',
            units        = '1/40MHz',
            offset       = 0x0,
            bitSize      = 16, 
            mode         = 'RW',
        ))  
        
        self.add(pr.LinkVariable(
            name         = 'CalPulseDelayNs', 
            units        = 'ns',
            disp         = '{:d}',
            dependencies = [self.CalPulseDelay],
            linkedGet    = lambda: (self.CalPulseDelay.value()+1)*25,
        ))    

        self.add(pr.RemoteVariable(
            name         = 'CalPulseWidth', 
            description  = 'cal pulse width (includes zero)',
            units        = '1/160MHz',
            offset       = 0x0,
            bitSize      = 16, 
            bitOffset    = 16, 
            mode         = 'RW',
        ))  
        
        self.add(pr.LinkVariable(
            name         = 'CalPulseWidthNs', 
            units        = 'ns',            
            disp         = '{:1.2f}',
            dependencies = [self.CalPulseWidth],
            linkedGet    = lambda: self.CalPulseWidth.value()*6.25,
        ))            

        self.add(pr.RemoteVariable(
            name         = 'CalPulseCount', 
            description  = 'Number of cal pulses per software trigger (zero inclusive)',
            offset       = 0x4,
            bitSize      = 16, 
            mode         = 'RW',
        ))          
                    
        self.add(pr.RemoteCommand(   
            name         = 'Start',
            description  = 'Triggers cal pulse train sequence',
            offset       = 0x8,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne
            # function     = lambda cmd: cmd.post(1),
        ))
       
        self.add(pr.RemoteVariable(
            name         = 'Continuous', 
            description  = 'continuous run the cal pulse train',
            offset       = 0xC,
            bitSize      = 1, 
            mode         = 'RW',      
        ))          
