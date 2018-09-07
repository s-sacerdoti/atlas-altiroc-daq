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

import pyrogue
import pyrogue.interfaces.simulation
import pyrogue.protocols

import axipcie as pcie
import surf.protocols.pgp as pgp
  
class Pcie(pyrogue.Device):
    def __init__(   self,       
            name        = "Pcie",
            description = "Container for FPGA",
            dev         = '/dev/datadev_0',
            hwEmu       = False,
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        ######################################################################
        
        # Check if emulating the GUI interface
        if (hwEmu):
            # Create emulated hardware interface
            print ("Running in Hardware Emulation Mode:")
            srp = pyrogue.interfaces.simulation.MemEmulate()
            
        else:
            # Create the stream interface
            memMap = rogue.hardware.axi.AxiMemMap(dev)         
            
        ######################################################################
        self.add(pcie.AxiPcieCore(
            memBase = memMap ,
            offset  = 0x00000000, 
            expand  = False, 
        ))
        
        for i in range(8):
            self.add(pgp.Pgp3AxiL( 
                memBase         = memMap,
                name            = ('Pgp3Mon[%d]' % i),
                offset          = (0x00800000 + i*0x10000),  
                numVc           = 16,
                writeEn         = True,
                expand          = False,
            ))
            