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
import numpy as np
import common as feb

#rogue.Logging.setLevel(rogue.Logging.Debug)


#################################################################

class MyEventReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)

        
    def _acceptFrame(self,frame):
        # Get the payload data
        p = bytearray(frame.getPayload())
        # Return the buffer index
        frame.read(p,0)
        # Check for a modulo of 32-bit word 
        if ((len(p) % 4) == 0):
            count = int(len(p)/4)
            # Combine the byte array into single 32-bit word
            hitWrd = np.frombuffer(p, dtype='uint32', count=count)
            # Loop through each 32-bit word
            for i in range(count):
                # Parse the 32-bit word
                dat = ParseDataWord(hitWrd[i])
                # Print the event if hit
                if (dat.Hit > 0):                
                    # Print the event
                    print( 'Event[SeqCnt=0x%x]: (TotOverflow = %r, TotData = 0x%x), (ToaOverflow = %r, ToaData = 0x%x), hit=%r' % (
                            dat.SeqCnt,
                            dat.TotOverflow,
                            dat.TotData,
                            dat.ToaOverflow,
                            dat.ToaData,
                            dat.Hit,
                    ))        
                
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
dataStream = MyEventReader()    
pyrogue.streamTap(top.dataStream, dataStream) 

# Start the system
top.start(initRead=True)

# Load the default YAML file
top.ReadConfig(arg='config/test.yml')

# Setup the pulser generator 
top.Asic.PulseTrain.PulseCount.set(0x1)
top.Asic.PulseTrain.PulseWidth.set(0x1)
top.Asic.PulseTrain.PulsePeriod.set(0x10)
top.Asic.PulseTrain.Continuous.set(0x0)

for i in range(1024):
    if (i%0x10 == 0):
        print (i)

    # Initializing the ASIC
    top.Asic.Gpio.RSTB_RAM.set(0x0)
    top.Asic.Gpio.RSTB_READ.set(0x0)
    top.Asic.Gpio.RSTB_TDC.set(0x0)
    top.Asic.Gpio.RSTB_RAM.set(0x1)
    top.Asic.Gpio.RSTB_READ.set(0x1)
    top.Asic.Gpio.RSTB_TDC.set(0x1)
    
    # Update the programmable delay
    top.SysReg.DlyData.set(i)

    # Send the CMD_PULSE/EXT_TRIG
    top.Asic.PulseTrain.OneShot()

# Wait for the data
time.sleep(1)

# Close
top.stop()
