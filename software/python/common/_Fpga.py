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

import surf.axi             as axi
import surf.xilinx          as xil
import surf.devices.micron  as prom
import surf.devices.linear  as linear
import surf.devices.nxp     as nxp
import surf.devices.silabs  as silabs
import surf.ethernet.udp    as udp

import common

class MyAxiVersion(axi.AxiVersion):
    def __init__(self,
            name             = 'MyAxiVersion',
            description      = 'AXI-Lite Version Module',
            numUserConstants = 0,
            **kwargs):
            
        super().__init__(
            name        = name, 
            description = description, 
            **kwargs
        )
        
        self.add(pr.RemoteVariable(   
            name         = "MacAddress",
            description  = "MacAddress (big-Endian configuration)",
            offset       = 0x400,
            bitSize      = 48,
            mode         = "RO",
            hidden       = True,
        ))
        
        self.add(pr.LinkVariable(
            name         = "MAC_ADDRESS", 
            description  = "MacAddress (human readable)",
            mode         = 'RO', 
            linkedGet    = udp.getMacValue,
            dependencies = [self.variables["MacAddress"]],
        ))          

class Fpga(pr.Device):
    def __init__(   
        self,       
        name        = 'Fpga',
        description = 'Container for FPGA registers',
        configProm  = False,
        advanceUser = False,
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)

        self.add(MyAxiVersion( 
            name    = 'AxiVersion', 
            offset  = 0x00000000, 
            expand  = False,
        ))
        
        if(configProm):
            self.add(prom.AxiMicronN25Q(
                name    = 'AxiMicronN25Q', 
                offset  = 0x00020000, 
                hidden  = True, # Hidden in GUI because indented for scripting
            ))
        
        if(advanceUser):
        
            self.add(xil.Xadc(
                name    = 'Xadc', 
                offset  = 0x00010000, 
                expand  = False,
                hidden  = True, # Hidden in GUI because indented for scripting
            ))
        
            self.add(nxp.Sa56004x(      
                name        = 'BoardTemp', 
                description = 'This device monitors the board temperature and FPGA junction temperature', 
                offset      = 0x00040000, 
                expand      = False,
                hidden      = True, # Hidden in GUI because indented for scripting
            ))
            
            self.add(linear.Ltc4151(
                name        = 'BoardPwr', 
                description = 'This device monitors the board power, input voltage and input current', 
                offset      = 0x00040400, 
                senseRes    = 20.E-3, # Units of Ohms
                expand      = False,
                hidden      = True, # Hidden in GUI because indented for scripting
            ))

            self.add(nxp.Sa56004x(      
                name        = 'DelayIcTemp', 
                description = 'This device monitors the board temperature and Delay IC\'s temperature', 
                offset      = 0x00050000, 
                expand      = False,
                hidden      = True, # Hidden in GUI because indented for scripting
            ))        
    
            self.add(silabs.Si5345(      
                name        = 'Pll', 
                description = 'This device contains Jitter cleaner PLL', 
                offset      = 0x00070000, 
                expand      = False,
            ))     
        else:
            self.add(silabs.Si5345Lite(      
                name        = 'Pll', 
                description = 'This device contains Jitter cleaner PLL', 
                offset      = 0x00070000, 
                expand      = False,
            ))     
            
        self.add(common.Dac(
            name        = 'Dac', 
            description = 'This device contains DAC that sets the VTH', 
            offset      = 0x00060000, 
            expand      = False,
        ))        

        self.add(common.Altiroc(
            name        = 'Asic', 
            description = 'This device contains all the ASIC control/monitoring', 
            offset      = 0x01000000, 
            asyncDev    = [self.Pll.Locked], # Only allow access after the PLL is locked
            expand      = True,
        ))
