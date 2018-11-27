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
            name        = 'SlowControl', 
            description = 'This device contains Altiroc ASIC\'s slow control shift register interface',
            offset      = 0x00010000, 
            expand      = False,
        ))    

        self.add(common.AltirocProbe(
            name        = 'Probe', 
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
            bitSize      = 3, 
            mode         = 'RW',
            enum        = {
                0x0: 'Disabled', 
                0x1: '20MHz', 
                0x2: '10MHz', 
                0x3: '5MHz', 
                0x4: '2.5MHz', 
                0x5: '1.25MHz',                 
            },
        ))

        self.add(pr.RemoteVariable(
            name         = 'DeserSampleEdge', 
            description  = 'Selects whether the rising edge or falling edge sample is used in the deserializer',
            offset       = 0x900,
            bitSize      = 1, 
            mode         = 'RW',
            enum        = {
                0x0: 'RisingEdge', 
                0x1: 'FallingEdge',               
            },
        ))  

        self.add(pr.RemoteVariable(
            name         = 'EmuEnable', 
            description  = 'Enables the emulation mode where a streaming data hit message will be generated for every pulse from the pulse generator',
            offset       = 0x904,
            bitSize      = 1, 
            mode         = 'RW',
        )) 


        self.add(pr.RemoteVariable(
            name         = 'RunEnable', 
            description  = 'Enables the normal stream data taking mode.',
            offset       = 0x908,
            bitSize      = 1, 
            mode         = 'RW',
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'PulseCount', 
            description  = '# of pulses in the one-shot pulse train',
            units        = '# of pulses',
            offset       = 0xA00,
            bitSize      = 16, 
            mode         = 'RW',
        ))

        self.add(pr.RemoteVariable(
            name         = 'PulseWidth', 
            description  = 'Pulse width of the pulses in the pulse train',
            units        = '1/40MHz',
            offset       = 0xA04,
            bitSize      = 16, 
            mode         = 'RW',
        ))
        
        self.add(pr.RemoteVariable(
            name         = 'PulsePeriod', 
            description  = 'period between pusles in the pulse train',
            units        = '1/40MHz',
            offset       = 0xA08,
            bitSize      = 16, 
            mode         = 'RW',
        )) 

        self.add(pr.LinkVariable(
            name         = 'PulseFreq', 
            description  = 'frequency of the pulse train',
            mode         = 'RO', 
            units        = 'Hz',
            linkedGet    = self.convtFreq,
            disp         = '{:.1e}',
            dependencies = [self.variables['PulsePeriod']],
        ))           
        
        self.add(pr.RemoteVariable(
            name         = 'Continuous', 
            description  = 'Sets the pulse train module into continuous mode',
            offset       = 0xA0C,
            bitSize      = 1, 
            mode         = 'RW',
        ))        
        
        self.add(pr.RemoteCommand(   
            name         = 'OneShot',
            description  = 'One shot trigger for pulse train',
            offset       = 0xA10,
            bitSize      = 1,
            bitOffset    = 0,
            base         = pr.UInt,
            function     = lambda cmd: cmd.post(1),
            hidden       = False,
        ))

        
    @staticmethod
    def convtFreq(var):
        value = int(var.dependencies[0].value())
        if (value <= 0):
            return 0.0
        else:
            value = 40.0E+6/float(value)
            return value