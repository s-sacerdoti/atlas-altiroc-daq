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
import pyrogue as pr
import pyrogue.gui
import argparse
import time
import common as feb

#################################################################

# Set the argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument(
    "--ip", 
    nargs    ='+',
    required = True,
    help     = "List of IP addresses",
)  

parser.add_argument(
    "--mcs", 
    type     = str,
    required = True,
    help     = "path to mcs file",
)

# Get the arguments
args = parser.parse_args()

#################################################################

# Setup root class
top = feb.Top(
    ip          = args.ip,
    pollEn      = False,
    initRead    = False, 
    configProm  = True,
)    
    
# Loop through the devices
for i in range(top.numEthDev):    
    
    # Create useful pointers
    AxiVersion = top.Fpga[i].AxiVersion
    PROM       = top.Fpga[i].AxiMicronN25Q

    print ( '###################################################')
    print ( '#                 Old Firmware                    #')
    print ( '###################################################')
    AxiVersion.printStatus()

    # Program the FPGA's PROM
    PROM.LoadMcsFile(args.mcs)

    if(PROM._progDone):
        print('\nReloading FPGA firmware from PROM ....')
        AxiVersion.FpgaReload()
        time.sleep(10)
        print('\nReloading FPGA done')

        print ( '###################################################')
        print ( '#                 New Firmware                    #')
        print ( '###################################################')
        AxiVersion.printStatus()
    else:
        print('Failed to program FPGA')

top.stop()
exit()
