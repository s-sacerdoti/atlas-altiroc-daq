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

import sys
import rogue
import time
import random
import argparse

import pyrogue as pr
import pyrogue.gui
import common as feb

#rogue.Logging.setLevel(rogue.Logging.Debug)

#################################################################

# Set the argument parser
parser = argparse.ArgumentParser()

# Convert str to bool
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']

# Add arguments
parser.add_argument(
    "--ip", 
    type     = str,
    required = True,
    help     = "IP address",
)  

# Get the arguments
args = parser.parse_args()

#################################################################

# Setup root class
top = feb.Top(hwType='eth',ip= args.ip)    

# Tap the streaming data interface (same interface that writes to file)
dataStream = feb.ExampleEventReader()    
pyrogue.streamTap(top.dataStream, dataStream) 

# Start the system
top.start(initRead=True)

# Load the default YAML file
top.ReadConfig(arg='config/defaults.yml')

# Print the AXI Version build information
top.AxiVersion.printStatus()

# Use the emulation mode to generate for "fake" hit messages
top.Asic.EmuEnable.set(0x1)
top.Asic.PulseCount.set(0x4)
top.Asic.PulseWidth.set(0x1)
top.Asic.PulsePeriod.set(0x10)
top.Asic.Continuous.set(0x0)
top.Asic.OneShot()
top.Asic.EmuEnable.set(0x0)
time.sleep(0.1)

# Reset the ASIC
print ('Send a 1 second Reset pulse to all ASIC reset lines')
top.Asic.RSTB_RAM.set(0x0)
top.Asic.RSTB_READ.set(0x0)
top.Asic.RSTB_TDC.set(0x0)
top.Asic.RSTB_COUNTER.set(0x0)
time.sleep(1.0)
top.Asic.RSTB_RAM.set(0x1)
top.Asic.RSTB_READ.set(0x1)
top.Asic.RSTB_TDC.set(0x1)
top.Asic.RSTB_COUNTER.set(0x1)

# Ramp up the DAC
for i in range(2**16):
    if ( (i % 0x7) == 0 ):
        top.Dac.RawValue.set(i)
    if ( (i % 0xFFF) == 0 ):
        print( f'FPGA\'s DAC.Value[{i}]' )
print( f'FPGA\'s DAC.Value[{i}]' )

# Set a random number to scratch pad register
randValue = random.randint(0, 0xFFFFFFFF)
print( f'randValue.set[{randValue}]' )
top.AxiVersion.ScratchPad.set(randValue)
print( 'randValue.get(%d)' % top.AxiVersion.ScratchPad.get() )

# Example of creating a pointer to a python device then ramping up the DAC
sc = top.Asic.SlowControl
for i in range(2**10):
    sc.dac.set(i)
    if ( (i % 0xFF) == 0 ):
        print( f'ASIC\'s DAC.Value[{i}]' )
print( f'ASIC\'s DAC.Value[{i}]' )

# Close
top.stop()
