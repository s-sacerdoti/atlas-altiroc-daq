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
import click

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
            disp         = '{:d}',
            pollInterval = 1,
        ))   
        
        self.add(pr.RemoteVariable(
            name         = 'BncExtTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x04,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        )) 

        self.add(pr.RemoteVariable(
            name         = 'LocalMasterTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x08,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'RemoteSlaveTrigDropCnt', 
            description  = 'Increments every time a trigger is dropped due to previous readout cycle not being completed (renable still active)',
            offset       = 0x0C,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'CalPulseTrigCnt', 
            description  = 'Increments every time a trigger is received for readout (renable not active)',
            offset       = 0x10,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))   
        
        self.add(pr.RemoteVariable(
            name         = 'BncExtTrigCnt', 
            description  = 'Increments every time a trigger is received for readout (renable not active)',
            offset       = 0x14,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        )) 

        self.add(pr.RemoteVariable(
            name         = 'LocalMasterTrigCnt', 
            description  = 'Increments every time a trigger is received for readout (renable not active)',
            offset       = 0x18,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'RemoteSlaveTrigCnt', 
            description  = 'Increments every time a trigger is received for readout (renable not active)',
            offset       = 0x1C,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'TriggerCnt', 
            description  = 'Increments every time a trigger is received for readout from any source',
            offset       = 0x20,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))       

        self.add(pr.RemoteVariable(
            name         = 'TriggerDropCnt', 
            description  = 'Increments every time a trigger is dropped',
            offset       = 0x24,
            bitSize      = 32, 
            mode         = 'RO',
            disp         = '{:d}',
            pollInterval = 1,
        ))   

        self.add(pr.RemoteVariable(
            name         = 'TimeCounter', 
            description  = 'Increments every 160 MHz clock cycle and reset to zero when PLL is not locked',
            offset       = 0x28,
            bitSize      = 64, 
            mode         = 'RO',
            units        = '1/160MHz',
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
            name         = 'CalStrobeAlign', 
            description  = 'Cal Pulse 40 MHz strobe alignment correction',
            units        = '1/160MHz',
            offset       = 0x44,
            bitSize      = 2, 
            bitOffset    = 0, 
            mode         = 'RW',
        ))
        
        self.add(pr.RemoteVariable(
            name         = 'TrigStrobeAlign', 
            description  = 'Trigger window 25 ns (40 MHz strobe) alignment correction',
            units        = '1/160MHz',
            offset       = 0x44,
            bitSize      = 2, 
            bitOffset    = 8, 
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
            name         = 'ReadoutStartDly', 
            description  = 'Delay between trigger and asserting RENBLE',
            offset       = 0x50,
            bitSize      = 16, 
            bitOffset    = 0, 
            mode         = 'RW',     
        )) 

        self.add(pr.LinkVariable(
            name         = 'ReadoutStartDlyNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.ReadoutStartDly],
            linkedGet    = common.getNsValue,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'TrigSizeBeforePause', 
            description  = 'Number of trigger event before pausing for oscilloscope dead time',
            offset       = 0x50,
            bitSize      = 16, 
            bitOffset    = 16,
            disp         = '{:d}',
            mode         = 'RW',     
        ))         

        self.add(pr.RemoteVariable(
            name         = 'TrigSizeBeforePauseCnt', 
            description  = 'Counter for the triggers events before pausing for oscilloscope dead time',
            offset       = 0x5C,
            bitSize      = 16, 
            disp         = '{:d}',
            mode         = 'RO',
            pollInterval = 1,
        ))   
        
        self.add(pr.RemoteVariable(
            name         = 'DeadtimeDuration', 
            description  = 'Deadtime duration for oscilloscope to catch up without readout',
            offset       = 0x54,
            bitSize      = 8, 
            bitOffset    = 0,             
            mode         = 'RW',
            disp         = '{:d}',
            units        = 'seconds',
        ))    

        self.add(pr.RemoteVariable(
            name         = 'BusyPulseWidth', 
            description  = 'Pulse width of BNC busy',
            offset       = 0x54,
            bitSize      = 8, 
            bitOffset    = 8,             
            mode         = 'RW',
            disp         = '{:d}',
            units        = '1/160MHz',
        ))

        self.add(pr.LinkVariable(
            name         = 'BusyPulseWidthNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.BusyPulseWidth],
            linkedGet    = common.getNsValue,
        ))
       
        self.add(pr.RemoteVariable(
            name         = 'DeadtimeCnt', 
            description  = 'Deadtime duration',
            offset       = 0x58,
            bitSize      = 8, 
            bitOffset    = 8, 
            mode         = 'RO',
            disp         = '{:d}',
            units        = 'seconds',            
            pollInterval = 1,
        ))       
       
        self.add(pr.RemoteVariable(
            name         = 'TrigState', 
            description  = 'Trigger FSM state',
            offset       = 0x58,
            bitSize      = 2, 
            bitOffset    = 0, 
            mode         = 'RO',
            pollInterval = 1,
            enum         = {
                0x0: 'IDLE_S', 
                0x1: 'READ_DLY_S', 
                0x2: 'READOUT_S', 
                0x3: 'OSCOPE_DEADTIME_S', 
            },
        ))

        self.add(pr.RemoteVariable(
            name         = 'BncExtTrig', 
            description  = 'current value of BNC External Trigger',
            offset       = 0x60,
            bitSize      = 1, 
            bitOffset    = 0, 
            mode         = 'RO',
            pollInterval = 1,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'LocalPcieToaBusy', 
            description  = 'current value of local PCIe TOA busy (active HIGH)',
            offset       = 0x60,
            bitSize      = 1, 
            bitOffset    = 1, 
            mode         = 'RO',
            pollInterval = 1,
        ))   

        self.add(pr.RemoteVariable(
            name         = 'LemoIn', 
            description  = 'current value LEMO input (active HIGH)',
            offset       = 0x60,
            bitSize      = 1, 
            bitOffset    = 2, 
            mode         = 'RO',
            pollInterval = 1,
        ))  

        self.add(pr.RemoteVariable(
            name         = 'OrTrig', 
            description  = 'current value of OR trigger logic',
            offset       = 0x60,
            bitSize      = 1, 
            bitOffset    = 3, 
            mode         = 'RO',
            pollInterval = 1,
        ))   

        self.add(pr.RemoteVariable(
            name         = 'AndTrig', 
            description  = 'current value of AND trigger logic',
            offset       = 0x60,
            bitSize      = 1, 
            bitOffset    = 4, 
            mode         = 'RO',
            pollInterval = 1,
        ))           
       
        self.add(pr.RemoteVariable(
            name         = 'EnableReadout', 
            description  = 'Enable the triggers to start the readout process',
            offset       = 0x80,
            bitSize      = 1, 
            mode         = 'RW',   
        ))               
       
        self.add(pr.RemoteCommand(   
            name         = 'CountReset',
            description  = 'Status counter reset',
            offset       = 0xFC,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne
        ))        
    
    def countReset(self):
        click.secho(f'{self.path}.countReset()', bg='cyan')
        self.CountReset()
        
