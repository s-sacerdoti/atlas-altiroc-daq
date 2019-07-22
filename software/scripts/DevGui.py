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
import time
import threading

#################################################################

Keep_display_alive = True
Live_display_interval = 1

#################################################################
def runLiveDisplay(event_display,fpga_index):
    while(Keep_display_alive):
        if event_display.has_new_data:
            event_display.refreshDisplay()
        time.sleep(Live_display_interval)
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
    "--loadYaml", 
    type     = argBool,
    required = False,
    default  = True,
    help     = "Enable loading of the defaults at start",
)  

parser.add_argument(
    "--printEvents", 
    type     = argBool,
    required = False,
    default  = False,
    help     = "prints the stream data event frames",
)  

parser.add_argument(
    "--liveDisplay", 
    type     = argBool,
    required = False,
    default  = False,
    help     = "Displays live plots of pixel information",
)  

# Get the arguments
args = parser.parse_args()

#################################################################

# Setup root class
print(args.ip)
top = feb.Top(
    ip       = args.ip,
    pollEn   = args.pollEn,
    initRead = args.initRead,       
    loadYaml = args.loadYaml,       
)    

# Create the Event reader streaming interface
if (args.printEvents):
    eventReader = feb.PrintEventReader()

    # Connect the file reader to the event reader
    pr.streamConnect(top.dataStream[0], eventReader) 

# Create Live Display
live_display_reset = []
if args.liveDisplay:
    for fpga_index in range( len(args.ip) ):
        # Create the fifo to ensure there is no back-pressure
        fifo = rogue.interfaces.stream.Fifo(100, 0, True)
        # Connect the device reader ---> fifo
        pr.streamConnect(top.dataStream[fpga_index], fifo) 
        # Create the pixelreader streaming interface
        event_display = feb.onlineEventDisplay(
                plot_title='FPGA ' + str(fpga_index),
                submitDir='display_snapshots',
                font_size=4,
                fig_size=(10,6),
                overwrite=True  )
        live_display_reset.append( event_display.reset )
        # Connect the fifo ---> stream reader
        pr.streamConnect(fifo, event_display) 
        # Retrieve pixel data streaming object
        display_thread = threading.Thread( target=runLiveDisplay, args=(event_display,fpga_index,) )
        display_thread.start()

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
Keep_display_alive = False
top.stop()
exit()   
