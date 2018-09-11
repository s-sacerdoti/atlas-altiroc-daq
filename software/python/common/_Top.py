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

import rogue
import rogue.hardware.axi
import rogue.utilities.fileio

import pyrogue
import pyrogue as pr
import pyrogue.protocols
import pyrogue.utilities.fileio
import pyrogue.interfaces.simulation

import surf.axi as axiVer
import surf.xilinx as xil
import surf.devices.micron as prom
import surf.devices.linear as linear
import surf.devices.nxp as nxp
import surf.devices.silabs as silabs

import common
        
class Top(pr.Root):
    def __init__(   self,       
            name        = "Top",
            description = "Container for FEB FPGA",
            hwType      = 'eth',
            ip          = '10.0.0.1',
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        # File writer
        self.dataWriter = pr.utilities.fileio.StreamWriter()
        self.add(self.dataWriter)
        
        ######################################################################
        
        if (hwType == 'simulation'):
            self.srpStream  = pr.interfaces.simulation.StreamSim(host='localhost', dest=0, uid=12, ssi=True)
            self.dataStream = pr.interfaces.simulation.StreamSim(host='localhost', dest=1, uid=12, ssi=True)      
        elif (hwType == 'eth'):
            self.rudp       = pr.protocols.UdpRssiPack(host=ip,port=8192,packVer=2)        
            self.srpStream  = self.rudp.application(0)
            self.dataStream = self.rudp.application(1)       
        # else:
            # # Catch exception  here 
                
                
        ######################################################################
        
        # Connect the SRPv3 to PGPv3.VC[0]
        self.memMap = rogue.protocols.srp.SrpV3()                
        pr.streamConnectBiDir( self.memMap, self.srpStream )             
                
        # Add data stream to file as channel to dataStream
        pr.streamConnect(self.dataStream,self.dataWriter.getChannel(0))            
            
        ######################################################################
        
        # Add devices
        self.add(axiVer.AxiVersion( 
            name    = 'AxiVersion', 
            memBase = self.memMap, 
            offset  = 0x00000000, 
            expand  = False,
        ))
        
        self.add(xil.Xadc(
            name    = 'Xadc', 
            memBase = self.memMap,
            offset  = 0x00010000, 
            expand  = False,
        ))
        
        self.add(prom.AxiMicronP30(
            name    = 'AxiMicronP30', 
            memBase = self.memMap, 
            offset  = 0x00020000, 
            hidden  = True, # Hidden in GUI because indented for scripting
        ))
        
        self.add(common.SysReg(
            name        = 'SysReg', 
            description = 'This device contains system level configuration and status registers', 
            memBase     = self.memMap, 
            offset      = 0x00030000, 
            expand      = False,
        ))
        
        self.add(nxp.Sa56004x(      
            name        = 'BoardTemp', 
            description = 'This device monitors the board temperature and FPGA junction temperature', 
            memBase     = self.memMap, 
            offset      = 0x00040000, 
            expand      = False,
        ))
        
        self.add(linear.Ltc4151(
            name        = 'BoardPwr', 
            description = 'This device monitors the board power, input voltage and input current', 
            memBase     = self.memMap, 
            offset      = 0x00040400, 
            senseRes    = 20.E-3, # Units of Ohms
            expand      = False,
        ))

        self.add(nxp.Sa56004x(      
            name        = 'DelayIcTemp', 
            description = 'This device monitors the board temperature and Delay IC\'s temperature', 
            memBase     = self.memMap, 
            offset      = 0x00050000, 
            expand      = False,
        ))        
        
        self.add(common.Dac(
            name        = 'Dac', 
            description = 'This device contains DAC that sets the VTH', 
            memBase     = self.memMap, 
            offset      = 0x00060000, 
            expand      = False,
        ))        
        
        self.add(silabs.Si5345(      
            name        = 'Pll', 
            description = 'This device contains Jitter cleaner PLL', 
            memBase     = self.memMap, 
            offset      = 0x00070000, 
            expand      = False,
        ))     

        self.add(common.Altiroc(
            name        = 'Asic', 
            description = 'This device contains all the ASIC control/monitoring', 
            memBase     = self.memMap, 
            offset      = 0x01000000, 
            expand      = False,
        ))           

        ######################################################################
        