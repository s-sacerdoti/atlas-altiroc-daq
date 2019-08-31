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
            
        # self.add(pr.RemoteVariable(
            # name         = 'StartPix', 
            # description  = 'Starting pixel for readout sequence',
            # offset       = 0x00,
            # bitSize      = 5, 
            # mode         = 'RW',
            # disp         = '{:d}',
        # ))

        # self.add(pr.RemoteVariable(
            # name         = 'LastPix', 
            # description  = 'Last pixel for readout sequence',
            # offset       = 0x04,
            # bitSize      = 5, 
            # mode         = 'RW',
            # disp         = '{:d}',
        # ))   

        self.add(pr.RemoteVariable(
            name         = 'RstRamPulseWidth', 
            description  = 'Sets the RSTB_READ pulse width (zero inclusive)',
            units        = '1/160MHz',
            offset       = 0x08,
            bitSize      = 12, 
            mode         = 'RW',
        ))        

        self.add(pr.LinkVariable(
            name         = 'RstRamPulseWidthNs', 
            units        = 'ns',
            disp         = '{:1.2f}',
            dependencies = [self.RstRamPulseWidth],
            linkedGet    = common.getNsValue,
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
            # description  = 'Number of RCK cycles per serialized word (zero inclusive) for not the first word',
            # offset       = 0x28,
            # bitSize      = 8, 
            # bitOffset    = 0, 
            # mode         = 'RO',
            # disp         = '{:d}',            
        # ))  

        # self.add(pr.RemoteVariable(
            # name         = 'BitSizeFirst', 
            # description  = 'Number of RCK cycles per serialized word (zero inclusive) for the first word',
            # offset       = 0x28,
            # bitSize      = 8, 
            # bitOffset    = 8, 
            # mode         = 'RO',
            # disp         = '{:d}',            
        # ))          

        # self.add(pr.RemoteVariable(
            # name         = 'TestPattern', 
            # description  = 'Force the data word to be all zeros with <01> marker',
            # offset       = 0x2C,
            # bitSize      = 1, 
            # mode         = 'RW',
        # ))            
        
        # self.add(pr.RemoteVariable(
            # name         = 'SendData', 
            # description  = '0x1: Send the data to software, 0x0: Drops the data',
            # offset       = 0x30,
            # bitSize      = 1, 
            # mode         = 'RW',
        # )) 

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
            disp         = '{:021b}',
            units        = 'binary',
            pollInterval = 1,
        ))             
        
        # self.add(pr.RemoteVariable(
            # name         = 'PolarityDout', 
            # description  = '1: Inverts the DOUT RX polarity, 0: non-inverted DOUT RX polarity',
            # offset       = 0x3C,
            # bitSize      = 1, 
            # mode         = 'RW',
        # )) 
        
        # self.add(pr.RemoteVariable(
            # name         = 'PolarityRck', 
            # description  = '1: Inverts RCK polarity, 0: non-inverted RCK polarity',
            # offset       = 0x3C,
            # bitSize      = 1, 
            # bitOffset    = 1, 
            # mode         = 'RW',
        # ))         

        # self.add(pr.RemoteVariable(
            # name         = 'TxDataBitReverse', 
            # description  = '1: reserves the TX data bit ordering, 0: no change to TX data bit ordering',
            # offset       = 0x40,
            # bitSize      = 1, 
            # mode         = 'RW',
        # )) 

        self.add(pr.RemoteVariable(
            name         = 'OnlySendFirstHit',
            description  = 'only Send First Hit',
            offset       = 0x44,
            bitSize      = 1, 
            mode         = 'RW',
        ))         
        
        self.add(pr.RemoteVariable(
            name         = 'EnProbeDigOutDisc', 
            description  = '1: enables the probe_dig_out_disc during the readout FSM',
            offset       = 0x48,
            bitSize      = 1, 
            mode         = 'RW',
        ))    

        self.add(pr.RemoteVariable(
            name         = 'EnProbeDigSelect', 
            description  = '1: selects en_probe_dig=EN_dout, 0: select this to be software control',
            offset       = 0x4C,
            bitSize      = 1, 
            bitOffset    = 5, 
            mode         = 'RW',
        ))   

        self.add(pr.RemoteVariable(
            name         = 'EnProbeDig', 
            description  = 'software control of en_probe_dig. Requires EnProbeDigSelect to be zero to take affect',
            offset       = 0x4C,
            bitSize      = 5, 
            bitOffset    = 0, 
            mode         = 'RW',
        ))  

        self.add(pr.RemoteVariable(
            name         = 'EnProbePa', 
            description  = '1: enables the probe_pa during the readout FSM (1-bit per pixel)',
            offset       = 0x50,
            bitSize      = 25,
            mode         = 'RW',
        ))          
        
        for i in range(5):
            for j in range(5):
                pixel = 5*i+j
                self.add(pr.RemoteVariable(
                    name         = f'RdIndexLut[{pixel}]', 
                    description  = 'Pixel Readout Index Lookup Table',
                    offset       = 0xE0 + 4*i,
                    bitSize      = 5, 
                    bitOffset    = 5*j, 
                    mode         = 'RW',
                    disp         = '{:d}',
                ))         
                
        self.add(pr.RemoteVariable(
            name         = 'ReadoutSize', 
            description  = 'Number of pixels to readout (zero inclusive)',
            offset       = 0xF4,
            bitSize      = 5, 
            mode         = 'RW',
            disp         = '{:d}',
        ))   
        
        self.add(pr.RemoteCommand(   
            name         = 'ForceStart',
            description  = 'Force a start of readout cycle',
            offset       = 0xF8,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne
        ))
        
        self.add(pr.RemoteCommand(   
            name         = 'SeqCntReset',
            description  = 'Resets the sequence counter',
            offset       = 0xFC,
            bitSize      = 1,
            function     = pr.BaseCommand.touchOne,
            hidden       = True,
        ))        
        
        @self.command()
        def SeqCntRst():   
            click.secho(f'{self.path}.SeqCntRst()', bg='cyan')
            self.SeqCntReset()
        