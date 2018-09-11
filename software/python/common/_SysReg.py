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
                    
        ##################
        # Status Registers 
        ##################    

        self.add(pr.RemoteVariable(
            name         = 'DlyLen', 
            description  = 'SY89295UMG LEN bit',
            offset       = 0x800,
            bitSize      = 1, 
            mode         = 'RW',
        ))
        
        self.add(pr.RemoteVariable(
            name         = 'DlyData', 
            description  = 'SY89295UMG Data bus',
            offset       = 0x800,
            bitSize      = 10, 
            mode         = 'RW',
            units        = '10ps',
        ))        

        self.add(pr.RemoteVariable(
            name         = 'RefClkSel', 
            description  = 'Reference Clock Select: Si5345.IN_SEL_REGCTRL must be 0x0 for CLKIN controlled by this else Si5345.IN_SEL controls the CLKIN MUXing',
            offset       = 0x808,
            bitSize      = 2, 
            mode         = 'RW',
            enum         = {
                0x0: 'IntClk', 
                0x1: 'ExtSmaClk', 
                0x2: 'ExtLemoClk',
            },
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
