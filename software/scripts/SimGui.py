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
import common as feb

# rogue.Logging.setLevel(rogue.Logging.Info)

#################################################################

# Setup root class
top = feb.Top(hwType='simulation')    

# Start the system
top.start(
    pollEn   = False,
    initRead = False,    
    timeout  = 5.0,    
)

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
