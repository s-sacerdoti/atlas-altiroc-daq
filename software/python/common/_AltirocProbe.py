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

class AltirocProbePix(pr.Device):
    def __init__(   
        self,       
        name        = "Pix",
        index       = 0,
        description = "Container for Altiroc ASIC Pixel Configuration",
            **kwargs):
            
        super().__init__(name=name,description=description,**kwargs)            
            
        def addReg(name,description,bitSize,bitOffset):

            downToBitOrdering = pr.UIntReversed 
            upToBitOrdering   = pr.UInt        

            remap = divmod((bitOffset-1),32)
            
            self.add(pr.RemoteVariable(  
                name        = name, 
                description = description,
                base        = upToBitOrdering,
                offset      = (remap[0]<<2),
                mode        = 'RW', 
                bitSize     = bitSize, 
                bitOffset   = remap[1],
                # value       = 0, # PROBES: Default value= all OFF (0)
            ))            
            
        addReg(
            name        = 'probe_pa',
            description = 'probe_pa',
            bitSize     = 1, 
            bitOffset   = (16+(29*index)),
        )
        
        addReg(
            name        = 'probe_vthc',
            description = 'analog_probe',
            bitSize     = 1, 
            bitOffset   = (17+(29*index)),
        )   

        addReg(
            name        = 'probe_dig_out_disc',
            description = 'digital_probe1',
            bitSize     = 1, 
            bitOffset   = (18+(29*index)),
        ) 

        addReg(
            name        = 'probe_toa',
            description = 'digital_probe2',
            bitSize     = 8, 
            bitOffset   = (19+(29*index)),
        ) 

        addReg(
            name        = 'probe_tot',
            description = 'digital_probe2',
            bitSize     = 10, 
            bitOffset   = (27+(29*index)),
        ) 

        addReg(
            name        = 'totf',
            description = 'digital_probe2',
            bitSize     = 2, 
            bitOffset   = (37+(29*index)),
        )   

        addReg(
            name        = 'tot_overflow',
            description = 'digital_probe2',
            bitSize     = 1, 
            bitOffset   = (39+(29*index)),
        )

        addReg(
            name        = 'toa_busy',
            description = 'digital_probe2',
            bitSize     = 1, 
            bitOffset   = (40+(29*index)),
        )   

        addReg(
            name        = 'toa_ready',
            description = 'digital_probe2',
            bitSize     = 1, 
            bitOffset   = (41+(29*index)),
        ) 

        addReg(
            name        = 'tot_busy',
            description = 'digital_probe2',
            bitSize     = 1, 
            bitOffset   = (42+(29*index)),
        )

        addReg(
            name        = 'tot_ready',
            description = 'digital_probe2',
            bitSize     = 1, 
            bitOffset   = (43+(29*index)),
        ) 

        addReg(
            name        = 'en_read',
            description = 'en_Ram_serializer',
            bitSize     = 1, 
            bitOffset   = (44+(29*index)),
        )                
        
class AltirocProbe(pr.Device):
    def __init__(   
        self,       
        name        = "AltirocProbe",
        description = "Container for Altiroc ASIC's probe shift register",
            **kwargs):
        
        super().__init__(name=name,description=description,**kwargs)
        
        def addProbeReg(name,description,bitSize,bitOffset):

            downToBitOrdering = pr.UIntReversed 
            upToBitOrdering   = pr.UInt        

            remap = divmod((bitOffset-1),32)
            
            self.add(pr.RemoteVariable(  
                name        = name, 
                description = description,
                base        = upToBitOrdering,
                offset      = (remap[0]<<2),
                mode        = 'RW', 
                bitSize     = bitSize, 
                bitOffset   = remap[1],
                # value     = 0, # PROBES: Default value= all OFF (0)
            ))         
        
        addProbeReg(
            name        = 'en_probe_pa', 
            description = 'block_analog_buffer_probe: column choice for probe_PA',
            bitSize     = 5, 
            bitOffset   = 1,
        )

        addProbeReg(
            name        = 'en_probe_dig', 
            description = 'block_digital_buffer_probe: column choice for digital_probe1', 
            bitSize     = 5, 
            bitOffset   = 6,
        ) 

        addProbeReg(
            name        = 'EN_dout', 
            description = '',
            bitSize     = 5, 
            bitOffset   = 11,
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

        def addPixReg(name,description,bitSize,bitOffset,device,index):

            downToBitOrdering = pr.UIntReversed 
            upToBitOrdering   = pr.UInt        

            remap = divmod((bitOffset-1),32)
            
            rawName = (f'pix{index}_'+name)
            
            self.add(pr.RemoteVariable(  
                name        = rawName, 
                description = description,
                base        = upToBitOrdering,
                offset      = (remap[0]<<2),
                mode        = 'RW', 
                bitSize     = bitSize, 
                bitOffset   = remap[1],
                hidden      = True,
                # value     = 0, # PROBES: Default value= all OFF (0)
            ))        
            
            rawVar = self.variables[rawName]
            
            device.add(pr.LinkVariable(
                name         = name,                 
                description  = description,
                mode         = 'RW', 
                linkedGet    = lambda: rawVar.value(),
                linkedSet    = lambda value, write: rawVar.set(value),
                dependencies = [rawVar],
                disp         = '0x{:x}',
            ))            
            
        for i in range(25):
        
            self.add(pr.Device(
                name        = f'pix[{i}]', 
                expand      = False,
            ))            
            
            pixDev = self.devices[f'pix[{i}]']
        
            addPixReg(
                name        = 'probe_pa',
                description = 'probe_pa',
                bitSize     = 1, 
                bitOffset   = (16+(29*i)),
                device      = pixDev,
                index       = i,
            )
            
            addPixReg(
                name        = 'probe_vthc',
                description = 'analog_probe',
                bitSize     = 1, 
                bitOffset   = (17+(29*i)),
                device      = pixDev,
                index       = i,
            )   

            addPixReg(
                name        = 'probe_dig_out_disc',
                description = 'digital_probe1',
                bitSize     = 1, 
                bitOffset   = (18+(29*i)),
                device      = pixDev,
                index       = i,
            ) 

            addPixReg(
                name        = 'probe_toa',
                description = 'digital_probe2',
                bitSize     = 8, 
                bitOffset   = (19+(29*i)),
                device      = pixDev,
                index       = i,
            ) 

            addPixReg(
                name        = 'probe_tot',
                description = 'digital_probe2',
                bitSize     = 10, 
                bitOffset   = (27+(29*i)),
                device      = pixDev,
                index       = i,
            )

            addPixReg(
                name        = 'totf',
                description = 'digital_probe2',
                bitSize     = 2, 
                bitOffset   = (37+(29*i)),
                device      = pixDev,
                index       = i,
            )  

            addPixReg(
                name        = 'tot_overflow',
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (39+(29*i)),
                device      = pixDev,
                index       = i,
            )

            addPixReg(
                name        = 'toa_busy',
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (40+(29*i)),
                device      = pixDev,
                index       = i,
            )   

            addPixReg(
                name        = 'toa_ready',
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (41+(29*i)),
                device      = pixDev,
                index       = i,
            )

            addPixReg(
                name        = 'tot_busy',
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (42+(29*i)),
                device      = pixDev,
                index       = i,
            )

            addPixReg(
                name        = 'tot_ready',
                description = 'digital_probe2',
                bitSize     = 1, 
                bitOffset   = (43+(29*i)),
                device      = pixDev,
                index       = i,
            )

            addPixReg(
                name        = 'en_read',
                description = 'en_Ram_serializer',
                bitSize     = 1, 
                bitOffset   = (44+(29*i)),
                device      = pixDev,
                index       = i,
            )            
