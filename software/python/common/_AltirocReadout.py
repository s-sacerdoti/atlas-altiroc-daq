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

class AltirocReadout(pr.Device):
    def __init__(   
        self,       
        name        = 'AltirocReadout',
        description = 'Container for Altiroc ASIC\'s Readout registers',
            **kwargs):
        
        super().__init__(
            name        = name,
            description = description,
            **kwargs)
            
        self.add(pr.RemoteVariable(
            name         = 'StartPix', 
            description  = 'Starting pixel for readout sequence',
            offset       = 0x00,
            bitSize      = 5, 
            mode         = 'RW',
            disp         = '{:d}',
        ))

        self.add(pr.RemoteVariable(
            name         = 'LastPix', 
            description  = 'Last pixel for readout sequence',
            offset       = 0x04,
            bitSize      = 5, 
            mode         = 'RW',
            disp         = '{:d}',
        ))   

        self.add(pr.RemoteVariable(
            name         = 'PixReadIteration', 
            description  = 'Sets the number of times that each pixel is readout (zero inclusive). Example: To readout all 400 samples in the ASIC buffer, set to PixReadIteration=399(0x18F)',
            offset       = 0x08,
            bitSize      = 9, 
            mode         = 'RW',
            disp         = '{:d}',
        ))           
        
        self.add(pr.RemoteVariable(
            name         = 'SeqCnt', 
            description  = 'Sequence counter that\'s in the header',
            offset       = 0x0C,
            bitSize      = 32, 
            mode         = 'RO',
            pollInterval = 1,
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'ProbeToRstDly', 
            description  = 'Sets the delay between completing the probe write to asserting the RST (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x10,
            bitSize      = 12, 
            mode         = 'RW',
        )) 

        self.add(pr.LinkVariable(
            name         = 'ProbeToRstDlyNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.ProbeToRstDly],
            linkedGet    = common.getNsValue,
        )) 

        self.add(pr.RemoteVariable(
            name         = 'RstPulseWidth', 
            description  = 'Sets the RSTB_READ pulse width (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x14,
            bitSize      = 12, 
            mode         = 'RW',
        ))        

        self.add(pr.LinkVariable(
            name         = 'RstPulseWidthNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.RstPulseWidth],
            linkedGet    = common.getNsValue,
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'RstToReadDly', 
            description  = 'Sets the delay between completing the RST to the start of serialization (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x18,
            bitSize      = 12, 
            mode         = 'RW',
        ))         
        
        self.add(pr.LinkVariable(
            name         = 'RstToReadDlyNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.RstToReadDly],
            linkedGet    = common.getNsValue,
        ))          
        
        self.add(pr.RemoteVariable(
            name         = 'RckHighWidth', 
            description  = 'Readout serialization Clock high phase width (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x1C,
            bitSize      = 12, 
            mode         = 'RW',
        ))     
        
        self.add(pr.LinkVariable(
            name         = 'RckHighWidthNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.RckHighWidth],
            linkedGet    = common.getNsValue,
        ))         

        self.add(pr.RemoteVariable(
            name         = 'RckLowWidth', 
            description  = 'Readout serialization Clock high phase width (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x20,
            bitSize      = 12, 
            mode         = 'RW',
        ))       

        self.add(pr.LinkVariable(
            name         = 'RckLowWidthNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.RckLowWidth],
            linkedGet    = common.getNsValue,
        ))      

        self.add(pr.LinkVariable(
            name         = 'RckFreq', 
            units        = 'MHz',
            disp         = '{:1.2f}',
            dependencies = [self.RckHighWidth,self.RckLowWidth],
            linkedGet    = common.getMhzValue,
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'RestoreProbeConfig', 
            description  = '0: leaves the probe registers in readout state.  1: restores the probe registers back to state before readout',
            offset       = 0x24,
            bitSize      = 1, 
            mode         = 'RW',
        ))   

        # self.add(pr.RemoteVariable(
            # name         = 'BitSize', 
            # description  = 'Number of RCK cycles per serialized word (zero inclusive)',
            # offset       = 0x28,
            # bitSize      = 8, 
            # mode         = 'RO',
            # disp         = '{:d}',            
        # ))    

        self.add(pr.RemoteVariable(
            name         = 'TestPattern', 
            description  = 'Force the data word to be all zeros with <01> marker',
            offset       = 0x2C,
            bitSize      = 1, 
            mode         = 'RW',
        ))            
        
        self.add(pr.RemoteVariable(
            name         = 'SendData', 
            description  = '0x1: Send the data to software, 0x0: Drops the data',
            offset       = 0x30,
            bitSize      = 1, 
            mode         = 'RW',
        )) 

        self.add(pr.RemoteVariable(
            name         = 'EnProbeWrite', 
            description  = 'Enable Readout FSM to write/update the PROBE registers',
            offset       = 0x34,
            bitSize      = 1, 
            mode         = 'RW',
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'TxDataDebug', 
            description  = 'The last deserialized word for debugging',
            offset       = 0x38,
            bitSize      = 21, 
            mode         = 'RO',
            disp         = '{0:b}',
            units        = 'binary',
            pollInterval = 1,
        ))             
        
        self.add(pr.RemoteVariable(
            name         = 'PolarityDout', 
            description  = '1: Inverts the DOUT RX polarity, 0: non-inverted DOUT RX polarity',
            offset       = 0x3C,
            bitSize      = 1, 
            mode         = 'RW',
        ))               
        
        self.add(pr.RemoteCommand(   
            name         = 'ForceStart',
            description  = 'Force a start of readout cycle',
            offset       = 0xF8,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne
        ))
        
        self.add(pr.RemoteCommand(   
            name         = 'SeqCntRst',
            description  = 'Resets the sequence counter',
            offset       = 0xFC,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne
        ))        
        