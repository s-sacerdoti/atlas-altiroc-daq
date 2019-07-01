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
    nargs    ='+',
    required = True,
    help     = "List of IP addresses",
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

parser.add_argument(
    "--printEvents", 
    type     = argBool,
    required = False,
    default  = False,
    help     = "prints the stream data event frames",
)  

# Get the arguments
args = parser.parse_args()

#################################################################

# Setup root class
print(args.ip)
print(args.pollEn)
print(args.initRead)
top = feb.Top(
    ip       = args.ip,
    pollEn   = args.pollEn,
    initRead = args.initRead,       
)    

if (args.printEvents):
    # Create the Event reader streaming interface
    eventReader = feb.ExampleEventReader()

    # Connect the file reader to the event reader
    pr.streamConnect(top.dataStream[0], eventReader) 

# Create GUI
appTop = pr.gui.application(sys.argv)
guiTop = pr.gui.GuiTop(group='rootMesh')
appTop.setStyle('Fusion')
guiTop.addTree(top)
guiTop.resize(600, 800)

print("Starting GUI...\n");

# Run GUI
appTop.exec_()    
    
# Close
top.stop()
exit()   
