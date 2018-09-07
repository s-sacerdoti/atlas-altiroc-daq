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

class SysReg(pr.Device):
    def __init__(   self,       
        name        = "SysReg",
        description = "Container for system registers",
        pollInterval = 1,
        **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)

        ##################
        # Status Registers 
        ##################

        self.add(pr.RemoteVariable(
            name         = 'IdlyCtrlRdyCnt', 
            description  = 'IDELAY controller ready counter',
            offset       = 0x0,
            bitSize      = 32, 
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        )) 
        
        self.add(pr.RemoteVariable(
            name         = 'PllLockedCnt', 
            description  = 'PLL Locked counter',
            offset       = 0x4,
            bitSize      = 32, 
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        ))            
            
        self.add(pr.RemoteVariable(
            name         = 'IdlyCtrlRdy', 
            description  = 'IDELAY controller ready status',
            offset       = 0x400,
            bitSize      = 1,
            bitOffset    = 0,             
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        )) 
        
        self.add(pr.RemoteVariable(
            name         = 'PllLocked', 
            description  = 'PLL Locked status',
            offset       = 0x400,
            bitSize      = 1,
            bitOffset    = 1,  
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        ))          
            
        self.add(pr.RemoteVariable(
            name         = 'RefClk160MHzFreq', 
            description  = 'Reference Clock Frequency',
            offset       = 0x404,
            bitSize      = 32, 
            mode         = 'RO',
            units        = "Hz", 
            disp         = '{:d}',
            base         = pr.UInt,
            pollInterval = pollInterval,
        ))
        
        ##################
        # Status Registers 
        ##################        
        
        self.add(pr.RemoteVariable(
            name         = 'RefClkSel', 
            description  = 'Reference Clock Select',
            offset       = 0x800,
            bitSize      = 2, 
            mode         = 'RW',
            enum         = {
                0x0: 'IntClk', 
                0x2: 'ExtSmaClk', 
                0x3: 'ExtLemoClk',
            },
        ))        
        
        self.add(pr.RemoteCommand(   
            name         = 'PllRst',
            description  = 'PLL Reset',
            offset       = 0x804,
            # bitSize      = 1,
            # base         = pr.UInt,
            function     = lambda cmd: cmd.toggle(cmd),
            hidden       = False,
        ))   

        self.add(pr.RemoteCommand(   
            name         = 'AsicRst',
            description  = 'ASIC Reset',
            offset       = 0x808,
            # bitSize      = 1,
            # base         = pr.UInt,
            function     = lambda cmd: cmd.toggle(cmd),
            hidden       = False,
        ))           
        
        self.add(pr.RemoteVariable(
            name         = 'TimerConfig', 
            description  = 'Batcher timer configuration',
            offset       = 0x80C,
            bitSize      = 16, 
            mode         = 'RW',
            units        = '6.4ns',
            base         = pr.UInt,
        ))   

        self.add(pr.RemoteVariable(
            name         = 'BatchSize', 
            description  = 'Number of 32-bit (4 bytes) words to batch together into a AXIS frame',
            offset       = 0x810,
            bitSize      = 16, 
            mode         = 'RW',
            units        = '4Bytes',
            base         = pr.UInt,
        ))           
        
        self.add(pr.RemoteVariable(  
            name        = 'EnAuxClk',
            description = 'Enable the 40 MHz clock on the DPORT AUX pin (required for remote board emulation)',
            offset      = 0x814, 
            bitSize     = 1, 
            base        = pr.Bool,
            mode        = 'RW',
        ))  

        self.add(pr.RemoteVariable(  
            name        = 'EnLocalEmu',
            description = 'Enable non-serializer local emulation mode (A.K.A. stand alone emulation mode)',
            offset      = 0x818, 
            bitSize     = 1, 
            base        = pr.Bool,
            mode        = 'RW',
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'RollOverEn', 
            description  = 'Rollover enable for status counters',
            offset       = 0xFF8,
            bitSize      = 2, 
            mode         = 'RW',
            base         = pr.UInt,
        ))        
        
        self.add(pr.RemoteCommand(   
            name         = 'CntRst',
            description  = 'Status counter reset',
            offset       = 0xFFC,
            bitSize      = 1,
            bitOffset    = 0x00,
            base         = pr.UInt,
            function     = lambda cmd: cmd.post(1),
            hidden       = False,
        ))  
