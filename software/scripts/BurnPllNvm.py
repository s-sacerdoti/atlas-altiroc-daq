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
import pyrogue as pr
import pyrogue.gui
import argparse
import common as feb

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

parser.add_argument(
    "--pollEn", 
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable auto-polling",
) 

parser.add_argument(
    "--initRead", 
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable read all variables at start",
)  

# Get the arguments
args = parser.parse_args()

#################################################################

# Setup root class
top = feb.Top(hwType='eth',ip=args.ip,configPll=True)    

# Start the system
top.start(
    pollEn    = args.pollEn,
    initRead  = args.initRead,
)

# Default PLL configuration file path
top.Pll.LoadCsvFile(arg='config/pll-config/Si5345-RevD-Registers.csv') 

# Write the volatile configuration into the non-volatile memory
top.Pll.Page0.NVM_WRITE.set(0xc7)
top.Pll.Page0.NVM_WRITE.set(0x0)
    
# Close
top.stop()
exit()   
