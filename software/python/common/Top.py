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

import rogue
import rogue.hardware.axi
import rogue.utilities.fileio

import pyrogue
import pyrogue as pr
import pyrogue.protocols
import pyrogue.utilities.fileio
import pyrogue.interfaces.simulation

import RceG3 as rceg3
import surf.axi as axiVer
import surf.xilinx as xil
import surf.devices.micron as prom
import surf.devices.linear as linear
import surf.devices.nxp as nxp
import surf.protocols.pgp as pgp

import axipcie as pcie

import common
        
class Top(pr.Root):
    def __init__(   self,       
            name        = "Top",
            description = "Container for FEB FPGA",
            dev         = '/dev/datadev_0',
            hwType      = 'pcie',
            ip          = '10.0.0.1',
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        # File writer
        dataWriter = pr.utilities.fileio.StreamWriter()
        self.add(dataWriter)
        
        ######################################################################
        
        if ( hwType == 'hsio-dtm' ) or ( hwType == 'rce-dpm' ):
            # Create the mmap interface
            rceMap = rogue.hardware.axi.AxiMemMap('/dev/rce_memmap')
            # Add RCE version device
            self.add(rceg3.RceVersion( 
                memBase = rceMap,
                expand  = False,
            ))               
            # Add PGPv3 to the FEB
            self.add(pgp.Pgp3AxiL( 
                name    = 'Pgp3Mon',
                memBase = rceMap,
                offset  = 0xA0000000,
                numVc   = 1,
                writeEn = True,
                expand  = False,
            ))    
            if ( hwType == 'hsio-dtm' ):
                # Add PGPv2b to the HSIO FPGA
                self.add(pgp.Pgp2bAxi( 
                    name    = 'Pgp2bMon',
                    memBase = rceMap,
                    offset  = 0xA1000000,
                    expand  = False,
                ))    
                # Connect the SRPv0 to PGPv2b.VC[1]
                pgp2bVc1  = rogue.hardware.axi.AxiStreamDma('/dev/axi_stream_dma_0',1,True)
                srpV0 = rogue.protocols.srp.SrpV0()                
                pr.streamConnectBiDir( srpV0, pgp2bVc1 )
                
                
        if ( hwType == 'pcie' ):

            axiMemMap = rogue.hardware.axi.AxiMemMap(dev)         
                
            self.add(pcie.AxiPcieCore(
                memBase = axiMemMap ,
                offset  = 0x00000000, 
                expand  = False, 
            ))
                
            # for i in range(8):
                # self.add(pgp.Pgp3AxiL( 
                    # memBase         = axiMemMap,
                    # name            = ('Pgp3Mon[%d]' % i),
                    # offset          = (0x00800000 + i*0x10000),  
                    # numVc           = 16,
                    # writeEn         = True,
                    # expand          = False,
                # ))                
                
                
        ######################################################################          
        
        # Create an empty stream arrays
        configStream = [None] * 4
        dataStream   = [None] * 4
        
        ########################################################################################################################
        # https://github.com/slaclab/rogue/blob/master/include/rogue/hardware/axi/AxiStreamDma.h
        # static boost::shared_ptr<rogue::hardware::axi::AxiStreamDma> create (std::string path, uint32_t dest, bool ssiEnable);
        ########################################################################################################################
    
        ######################################################################
        # PGPv3.[VC=0] = FEB SRPv3 Register Access
        # PGPv3.[VC=1] = RD53[DPORT=0] Streaming ASIC Configuration Interface
        # PGPv3.[VC=2] = RD53[DPORT=1] Streaming ASIC Configuration Interface
        # PGPv3.[VC=3] = RD53[DPORT=2] Streaming ASIC Configuration Interface
        # PGPv3.[VC=4] = RD53[DPORT=3] Streaming ASIC Configuration Interface
        # PGPv3.[VC=5] = RD53[DPORT=0] Streaming Data Interface
        # PGPv3.[VC=6] = RD53[DPORT=1] Streaming Data Interface
        # PGPv3.[VC=7] = RD53[DPORT=2] Streaming Data Interface
        # PGPv3.[VC=8] = RD53[DPORT=3] Streaming Data Interface
        ######################################################################
        
        if (hwType == 'simulation'):
            srpStream = pr.interfaces.simulation.StreamSim(host='localhost', dest=0, uid=12, ssi=True)
            for i in range(4):
                configStream[i] = pr.interfaces.simulation.StreamSim(host='localhost', dest=1+i, uid=12, ssi=True)     
                dataStream[i]   = pr.interfaces.simulation.StreamSim(host='localhost', dest=5+i, uid=12, ssi=True)     
        elif (hwType == 'eth'):
            rudp = pr.protocols.UdpRssiPack(host=ip,port=8192,packVer=2)        
            srpStream = rudp.application(0)
            for i in range(4):
                configStream[i] = rudp.application(1+i)
                dataStream[i]   = rudp.application(5+i)       
        else:
            srpStream = rogue.hardware.axi.AxiStreamDma(dev,0,True)        
            for i in range(4):
                configStream[i] = rogue.hardware.axi.AxiStreamDma(dev,1+i,True)
                dataStream[i]   = rogue.hardware.axi.AxiStreamDma(dev,5+i,True)
                
        ######################################################################
        
        # Connect the SRPv3 to PGPv3.VC[0]
        memMap = rogue.protocols.srp.SrpV3()                
        pr.streamConnectBiDir( memMap, srpStream )             
                
        for i in range(4):            
            # Add data stream to file as channel [i] to dataStream[i]
            pr.streamConnect(dataStream[i],dataWriter.getChannel(i))            
            
        ######################################################################
        
        # Add devices
        self.add(axiVer.AxiVersion( 
            name    = 'AxiVersion', 
            memBase = memMap, 
            offset  = 0x00000000, 
            expand  = False,
        ))
        
        self.add(xil.Xadc(
            name    = 'Xadc', 
            memBase = memMap,
            offset  = 0x00010000, 
            expand  = False,
        ))
        
        self.add(prom.AxiMicronP30(
            name    = 'AxiMicronP30', 
            memBase = memMap, 
            offset  = 0x00020000, 
            hidden  = True, # Hidden in GUI because indented for scripting
        ))
        
        self.add(common.SysReg(
            name        = 'SysReg', 
            description = 'This device contains system level configuration and status registers', 
            memBase     = memMap, 
            offset      = 0x00030000, 
            expand      = False,
        ))
        
        self.add(common.Ntc(
            name        = 'Rd53Ntc', 
            description = 'This device contains the four NTC MAX6682 readout modules', 
            memBase     = memMap, 
            offset      = 0x00040000, 
            expand      = False,
        ))
        
        self.add(nxp.Sa56004x(      
            name        = 'BoardTemp', 
            description = 'This device monitors the board temperature and FPGA junction temperature', 
            memBase     = memMap, 
            offset      = 0x00050000, 
            expand      = False,
        ))
        
        self.add(linear.Ltc4151(
            name        = 'BoardPwr', 
            description = 'This device monitors the board power, input voltage and input current', 
            memBase     = memMap, 
            offset      = 0x00050400, 
            senseRes    = 20.E-3, # Units of Ohms
            expand      = False,
        ))

        for i in range(4):
            self.add(common.RxPhy(
                name    = ('RxPhy[%d]'%i), 
                memBase = memMap, 
                offset  = (0x01000000*(i+1)), 
                expand  = False,
            ))             
        
        for i in range(4):
            self.add(common.RxPhyMon(
                name    = ('RxPhyMon[%d]'%i), 
                memBase = memMap, 
                offset  = (0x01000000*(i+1) + 0x00100000), 
                expand  = False,
            )) 
            
        ######################################################################
        