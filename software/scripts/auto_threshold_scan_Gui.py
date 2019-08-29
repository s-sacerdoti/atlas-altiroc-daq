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
Resync_interval = 0.25

#################################################################
def runLiveDisplay(event_display,fpga_index):
    while(Keep_display_alive):
        event_display.refreshDisplay()
        time.sleep(Live_display_interval)
#################################################################

def resync_sequence_counter(top):
    while(True):
        readout0 = top.Fpga[0].Asic.Readout
        readout1 = top.Fpga[1].Asic.Readout
        if readout0.SeqCnt != readout1.SeqCnt:
            print('Resynced!')
            readout0.SeqCntRst()
            readout1.SeqCntRst()
        time.sleep(Resync_interval)
#################################################################



def gui_thread():
    # Create GUI
    appTop = pr.gui.application(sys.argv)
    guiTop = pr.gui.GuiTop()
    appTop.setStyle('Fusion')
    guiTop.addTree(top)
    guiTop.resize(600, 800)

    #Run GUI
    print("Starting GUI...\n");
    appTop.exec_()
#################################################################


def run_auto_test(top):
    frames_to_record = 10000
    pixel_range = (6,7,8,10,12,13,14)
    threshold_value_range = range(380,650,50)
    for pixel_number in pixel_range:
        print('Enabling pixel '+str(pixel_number))
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x1)
        top.Fpga[0].Asic.Readout.StartPix = pixel_number
        top.Fpga[0].Asic.Readout.LastPix = pixel_number
        for threshold_value in threshold_value_range:
            filename = 'ThresholdScanData/data_thresholdScan_'+str(pixel_number)+'_'+str(threshold_value)+'.dat'
            try: os.remove(filename)
            except OSError: pass

            print('changing DAC10bit to ' + str(threshold_value))
            top.Fpga[0].Asic.SlowControl.DAC10bit = threshold_value
            top.dataWriter._writer.open(filename)
            top.Fpga[0].Asic.Trig.EnableReadout = 1

            print('File ' + filename + ' open, readout enabled, waiting for frames...')
            while  top.dataWriter.getFrameCount() < frames_to_record: pass
            print('Frames recieved. Disabling readout and closing file')

            top.Fpga[0].Asic.Trig.EnableReadout = 0
            top.dataWriter._writer.close()
        print('Disabling pixel ' + str(pixel_number))
        top.Fpga[0].Asic.SlowControl.EN_ck_SRAM[pixel_number].set(0x0)
        top.Fpga[0].Asic.SlowControl.disable_pa[pixel_number].set(0x1)
        top.Fpga[0].Asic.SlowControl.ON_discri[pixel_number].set(0x0)
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
    "--defaultFile", 
    type     = str,
    required = False,
    default  = 'config/defaults.yml',
    help     = "default configuration file to be loaded before user configuration",
)  

parser.add_argument(
    "--userYaml", 
    nargs    ='+',
    required = False,
    default  = [''],
    help     = "List of board specific configurations to be loaded after defaults",
)  

parser.add_argument(
    "--refClkSel", 
    type     = str,
    required = False,
    default  = 'IntClk',
    help     = "Selects the reference input clock for the jitter cleaner \
                PLL: IntClk = on-board OSC, ExtSmaClk = 50 Ohm SMA Clock, ExtLemoClk = 100Ohm diff pair Clock",
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

parser.add_argument(
    "--forceSeqResync", 
    type     = argBool,
    required = False,
    default  = True,
    help     = "Periodically forces a resync of the sequence counters",
)  

# Get the arguments
args = parser.parse_args()

#################################################################

# Setup root class
print(args.ip)
top = feb.Top(
    ip          = args.ip,
    pollEn      = args.pollEn,
    initRead    = args.initRead,       
    loadYaml    = args.loadYaml,       
    defaultFile = args.defaultFile,       
    userYaml    = args.userYaml,       
    refClkSel   = args.refClkSel,       
)    

# Create the Event reader streaming interface
if (args.printEvents): pr.streamTap(top.dataStream[0], feb.PrintEventReader() )

# Create Live Display
live_display_resets = []
if args.liveDisplay:
    for fpga_index in range( top.numEthDev ):
        # Create the fifo to ensure there is no back-pressure
        fifo = rogue.interfaces.stream.Fifo(100, 0, True)
        # Connect the device reader ---> fifo
        pr.streamTap(top.dataStream[fpga_index], fifo) 
        # Create the pixelreader streaming interface
        event_display = feb.onlineEventDisplay( plot_title='FPGA ' + str(fpga_index), submitDir='display_snapshots', font_size=4, fig_size=(14,7), overwrite=True  )
        #event_display = feb.beamTestEventDisplay( plot_title='FPGA ' +str(fpga_index), font_size=6, fig_size=(14,7) )
        live_display_resets.append( event_display.reset )
        # Connect the fifo ---> stream reader
        pr.streamConnect(fifo, event_display) 
        # Retrieve pixel data streaming object
        display_thread = threading.Thread( target=runLiveDisplay, args=(event_display,fpga_index,) )
        display_thread.start()
top.add_live_display_resets(live_display_resets)

if len( args.ip ) == 2 and args.forceSeqResync:
    resync_thread = threading.Thread( target=resync_sequence_counter, args=(top) )
    resync_thread.start()

guithread = threading.Thread( target=gui_thread )
guithread.start()

print('Auto-testing in 5...')
time.sleep(5)
run_auto_test(top)

# Close
Keep_display_alive = False
top.stop()
exit()   
