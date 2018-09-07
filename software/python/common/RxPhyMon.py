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

class RxPhyMon(pr.Device):
    def __init__(   self,       
        name        = "RxPhyMon",
        description = "Container for RX Phy Monitoring registers",
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
            name         = 'DataDropCnt',
            description  = 'Increments when data dropped due to back pressure',
            offset       = 0x000,
            bitSize      = 32,
            mode         = 'RO',
            pollInterval = pollInterval,
        )) 
        
        self.add(pr.RemoteVariable(
            name         = 'TimedOutCnt',
            description  = 'Increments when a batcher timed out event occurs',
            offset       = 0x004,
            bitSize      = 32, 
            mode         = 'RO',
            pollInterval = pollInterval,
        ))         
        
        self.addRemoteVariables(   
            name         = 'LinkUpCnt',
            description  = 'Status counter for link up',
            offset       = 0x008,
            bitSize      = 32,
            mode         = 'RO',
            number       = 4,
            stride       = 4,
            pollInterval = pollInterval,
        )

        self.add(pr.RemoteVariable(
            name         = 'ChBondCnt',
            description  = 'Status counter for channel bonding',
            offset       = 0x018,
            bitSize      = 32,
            mode         = 'RO',
            pollInterval = pollInterval,
        ))        
        
        self.add(pr.RemoteVariable(
            name         = 'LinkUp',
            description  = 'link up',
            offset       = 0x400,
            bitSize      = 4, 
            bitOffset    = 2,
            mode         = 'RO',
            pollInterval = pollInterval,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'ChBond',
            description  = 'channel bonding',
            offset       = 0x400,
            bitSize      = 1, 
            bitOffset    = 6,
            mode         = 'RO',
            pollInterval = pollInterval,
        ))  
        
        self.addRemoteVariables(   
            name         = 'AutoRead',
            description  = 'RD53 auto-read register',
            offset       = 0x410,
            bitSize      = 32,
            mode         = 'RO',
            number       = 4,
            stride       = 4,
            pollInterval = pollInterval,
        )   
        
        ##################
        # Status Registers 
        ##################        
        
        self.add(pr.RemoteVariable(
            name         = 'EnLane', 
            description  = 'Enable Lane Mask',
            offset       = 0x800,
            bitSize      = 4, 
            mode         = 'RW',
        )) 

        self.add(pr.RemoteVariable(
            name         = 'InvData', 
            description  = 'Invert the serial data bits',
            offset       = 0x804,
            bitSize      = 4, 
            mode         = 'RW',
        ))

        self.add(pr.RemoteVariable(
            name         = 'InvCmd', 
            description  = 'Invert the serial CMD bit',
            offset       = 0x808,
            bitSize      = 1, 
            mode         = 'RW',
        ))        
        
        self.add(pr.RemoteVariable(
            name         = 'RollOverEn', 
            description  = 'Rollover enable for status counters',
            offset       = 0xFF8,
            bitSize      = 7, 
            mode         = 'RW',
        ))        
        
        self.add(pr.RemoteCommand(   
            name         = 'CntRst',
            description  = 'Status counter reset',
            offset       = 0xFFC,
            bitSize      = 1,
            bitOffset    = 0x00,
            function     = lambda cmd: cmd.post(1),
            hidden       = False,
        ))  
