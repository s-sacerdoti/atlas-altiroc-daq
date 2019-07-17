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
import numpy as np
import time
import threading

#################################################################

Keep_display_alive = True
Live_display_interval = 1
Number_of_pixels = 25




#################################################################
def runLiveDisplay(pixel_data_list, event_display):
    while(Keep_display_alive):
        print('Start of loop')
        for pixel_data in pixel_data_list:
            toa_data = np.zeros(Number_of_pixels)
            tot_data = np.zeros(Number_of_pixels)
            hit_data = np.zeros(Number_of_pixels)
            for pixel in pixel_data:
                #if pixel.Hit and not pixel.ToaOverflow
                hit_data[pixel.PixelIndex] = pixel.Hit
                toa_data[pixel.PixelIndex] = pixel.ToaData
                #scale down tot data so we can use 128 bins for tot and toa
                tot_data[pixel.PixelIndex] = pixel.TotData/64
                event_display.updateData(toa_data, tot_data, hit_data)
            print(toa_data)
            print(tot_data)
            print(hit_data)
            print()
        print('Pixel data read or nonexistent')

        if len(pixel_data_list) > 0:
            pixel_data_list.clear()
            event_display.refreshDisplay()
        print('End of loop')
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
print(args.pollEn)
print(args.initRead)
top = feb.Top(
    ip       = args.ip,
    pollEn   = args.pollEn,
    initRead = args.initRead,       
)    

if (args.printEvents):
    # Create the Event reader streaming interface
    eventReader = feb.MyEventReader()

    # Connect the file reader to the event reader
    pr.streamConnect(top.dataStream[0], eventReader) 

# Create Live Display
if args.liveDisplay:
    # Create the fifo to ensure there is no back-pressure
    fifo = rogue.interfaces.stream.Fifo(100, 0, True)
    # Connect the device reader ---> fifo
    pr.streamConnect(top.dataStream[0], fifo) 
    # Create the pixelreader streaming interface
    dataStream = feb.MyPixelReader()
    # Connect the fifo ---> stream reader
    pr.streamConnect(fifo, dataStream) 
    # Retrieve pixel data streaming object
    pixel_data_list = dataStream.PixelData_list
    event_display = feb.onlineEventDisplay(
            submitDir='display_snapshots',font_size=4, fig_size=(10,6), overwrite=True  )
    display_thread = threading.Thread( target=runLiveDisplay, args=(pixel_data_list,event_display,) )
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
