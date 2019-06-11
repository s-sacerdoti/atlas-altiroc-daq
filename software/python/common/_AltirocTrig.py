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

class AltirocTrig(pr.Device):
    def __init__(   
        self,       
        name        = 'AltirocTrig',
        description = 'Container for Altiroc ASIC\'s Trigger registers',
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        self.add(pr.RemoteVariable(
            name         = 'CalPulseTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x00,
            bitSize      = 32, 
            mode         = 'RO',
            pollInterval = 1,
        ))   
        
        self.add(pr.RemoteVariable(
            name         = 'BncExtTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x04,
            bitSize      = 32, 
            mode         = 'RO',
            pollInterval = 1,
        )) 

        self.add(pr.RemoteVariable(
            name         = 'PcieLocalTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x08,
            bitSize      = 32, 
            mode         = 'RO',
            pollInterval = 1,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'LemoRemoteTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x0C,
            bitSize      = 32, 
            mode         = 'RO',
            pollInterval = 1,
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'TrigTypeSel', 
            description  = 'Selects whether this FPGA is a trigger master or slave',
            offset       = 0x40,
            bitSize      = 1, 
            mode         = 'RW',
            enum         = {
                0x0: 'Slave', 
                0x1: 'Master', 
            },            
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'StrobeAlign', 
            description  = '40 MHz strobe alignment correction',
            units        = '1/160MHz',
            offset       = 0x44,
            bitSize      = 2, 
            mode         = 'RW',
        ))
        
        self.add(pr.RemoteVariable(
            name         = 'EnCalPulseTrig', 
            description  = 'Mask for enabling cal pulse triggers',
            offset       = 0x48,
            bitSize      = 1, 
            bitOffset    = 0, 
            mode         = 'RW',
        ))

        self.add(pr.RemoteVariable(
            name         = 'EnBncExtTrig', 
            description  = 'Mask for enabling BNC external triggers',
            offset       = 0x48,
            bitSize      = 1, 
            bitOffset    = 1, 
            mode         = 'RW',
        ))  

        self.add(pr.RemoteVariable(
            name         = 'EnPcieLocalTrig', 
            description  = 'Mask for enabling PCIE Local triggers (TOA_BUSYB)',
            offset       = 0x48,
            bitSize      = 1, 
            bitOffset    = 2, 
            mode         = 'RW',
        ))   

        self.add(pr.RemoteVariable(
            name         = 'EnLemoRemoteTrig', 
            description  = 'Mask for enabling LEMO Remote triggers (TOA_BUSYB)',
            offset       = 0x48,
            bitSize      = 1, 
            bitOffset    = 3, 
            mode         = 'RW',
        ))   

        self.add(pr.RemoteVariable(
            name         = 'MasterModeSel', 
            description  = 'Selects whether the master FPGA using AND or OR for TOA_BUSY triggering',
            offset       = 0x4C,
            bitSize      = 1, 
            mode         = 'RW',
            enum         = {
                0x0: 'AND', 
                0x1: 'OR', 
            },            
        )) 

        self.add(pr.RemoteVariable(
            name         = 'TrigSizeBeforePause', 
            description  = 'Number of trigger event before pausing for oscilloscope dead time',
            offset       = 0x50,
            bitSize      = 16, 
            mode         = 'RW',     
        ))  

        self.add(pr.RemoteVariable(
            name         = 'DeadtimeDuration', 
            description  = 'Deadtime duration for oscilloscope to catch up without readout',
            offset       = 0x54,
            bitSize      = 8, 
            mode         = 'RW',   
            units        = 'seconds',
        ))          
       
        self.add(pr.RemoteVariable(
            name         = 'TrigState', 
            description  = 'Trigger FSM state',
            offset       = 0x58,
            bitSize      = 2, 
            mode         = 'RO',
            pollInterval = 1,
            enum         = {
                0x0: 'IDLE_S', 
                0x1: 'READOUT_S', 
                0x2: 'OSCOPE_DEADTIME_S', 
                0x3: 'RESERVED', 
            },
        ))        
       
        self.add(pr.RemoteCommand(   
            name         = 'CountReset',
            description  = 'Status counter reset',
            offset       = 0xFC,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne
        ))        
        
    def countReset(self):
        self.CountReset()
        