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

class AltirocProbe(pr.Device):
    def __init__(   
        self,       
        name        = "AltirocProbe",
        description = "Container for Altiroc ASIC's probe shift register",
            **kwargs):
        
        super().__init__(name=name,description=description,**kwargs)
        
        downToBitOrdering = pr.UIntReversed 
        upToBitOrdering   = pr.UInt        
        
        def addReg(name,description,bitSize,bitOffset):
            self.add(pr.RemoteVariable(  
                name        = name, 
                description = description,
                base        = upToBitOrdering,
                offset      = 0x000,
                mode        = 'RW', 
                bitSize     = bitSize, 
                bitOffset   = bitOffset-1,
                value       = 0, # PROBES: Default value= all OFF (0)
            ))
        
        addReg(
            name        = 'en_probe_pa', 
            description = 'block_analog_buffer_probe: column choice for probe_PA',
            bitSize     = 5, 
            bitOffset   = 1,
        )

        addReg(
            name        = 'en_probe_dig', 
            description = 'block_digital_buffer_probe: column choice for digital_probe1', 
            bitSize     = 5, 
            bitOffset   = 6,
        ) 

        addReg(
            name        = 'EN_dout', 
            description = '',
            bitSize     = 5, 
            bitOffset   = 11,
        )         
          
        ######################
        # Probe Configurations
        ######################
        
        for i in range(25):
        
            addReg(
                name        = ('probe_pa[%d]' % i), 
                description = 'probe_pa',
                bitSize     = 1, 
                bitOffset   = (16+(29*i)),
            )
            
            addReg(
                name        = ('probe_vthc[%d]' % i), 
                description = 'analog_probe',
                bitSize     = 1, 
                bitOffset   = (17+(29*i)),
            )   

            addReg(
                name        = ('probe_dig_out_disc[%d]' % i), 
                description = 'digital_probe1',
                bitSize     = 1, 
                bitOffset   = (18+(29*i)),
            ) 

            addReg(
                name        = ('probe_toa[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 8, 
                bitOffset   = (19+(29*i)),
            ) 

            addReg(
                name        = ('probe_tot[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 10, 
                bitOffset   = (27+(29*i)),
            ) 

            addReg(
                name        = ('totf[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 2, 
                bitOffset   = (37+(29*i)),
            )   

            addReg(
                name        = ('tot_overflow[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (39+(29*i)),
            )

            addReg(
                name        = ('toa_busy[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (40+(29*i)),
            )   

            addReg(
                name        = ('toa_ready[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (41+(29*i)),
            ) 

            addReg(
                name        = ('tot_busy[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (42+(29*i)),
            )

            addReg(
                name        = ('tot_ready[%d]' % i), 
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (43+(29*i)),
            ) 

            addReg(
                name        = ('en_read[%d]' % i), 
                description = 'en_Ram_serializer',
                bitSize     = 1, 
                bitOffset   = (44+(29*i)),
            )             

        self.add(pr.RemoteVariable(
            name         = 'rstL', 
            description  = 'Shift Register\'s reset (active LOW)',
            offset       = 0xFFC,
            bitSize      = 1, 
            mode         = 'RW',
            base         = pr.UInt,
            value        = 0x1,
        ))         
