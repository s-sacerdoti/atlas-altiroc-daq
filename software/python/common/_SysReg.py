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
            size        = (0x1 << 12), 
            **kwargs)

        ##################
        # Status Registers 
        ##################
        
        self.add(pr.RemoteVariable(
            name         = 'ExtPllLockedCnt', 
            description  = 'SiLab PLL Locked counter',
            offset       = 0x0,
            bitSize      = 32, 
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        ))            

        self.add(pr.RemoteVariable(
            name         = 'ExtPllLocked', 
            description  = 'SiLab PLL Locked status',
            offset       = 0x400,
            bitSize      = 1,
            bitOffset    = 0,  
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        )) 

        self.add(pr.RemoteVariable(
            name         = 'IntPllLockedCnt', 
            description  = 'FPGA PLL Locked counter',
            offset       = 0x0,
            bitSize      = 32, 
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        ))            

        self.add(pr.RemoteVariable(
            name         = 'IntPllLocked', 
            description  = 'FPGA PLL Locked status',
            offset       = 0x400,
            bitSize      = 1,
            bitOffset    = 1,  
            mode         = 'RO',
            base         = pr.UInt,
            pollInterval = pollInterval,
        ))         
        
        for i in range(2):
        
            self.add(pr.RemoteVariable(
                name         = f'PllToFpgaClkFreq[{i}]',
                offset       = (0x500 + (i*4)), 
                bitSize      = 32, 
                mode         = 'RO', 
                units        = "Hz",
                disp         = '{:d}',
                base         = pr.UInt,
                pollInterval = 1,
            ))        
                    
        ##################
        # Status Registers 
        ##################    
        
        self.add(pr.RemoteVariable(
            name         = 'DlyData', 
            description  = 'SY89295UMG Data bus',
            offset       = 0x804,
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
           
        # self.add(pr.RemoteVariable(
            # name         = 'FpgaPllRst', 
            # description  = 'FPGA\'s PLL reset',
            # offset       = 0x80C,
            # bitSize      = 1, 
            # mode         = 'RW',
            # base         = pr.UInt,
        # ))               
           
        self.add(pr.RemoteVariable(
            name         = 'RollOverEn', 
            description  = 'Rollover enable for status counters',
            offset       = 0xFF8,
            bitSize      = 1, 
            mode         = 'RW',
            base         = pr.UInt,
        ))        
        
    def countReset(self):
        self._rawWrite(offset=0xFFC,data=0x1)          
        