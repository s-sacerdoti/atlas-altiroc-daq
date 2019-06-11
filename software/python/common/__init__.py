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
from common._Altiroc            import *
from common._AltirocGpio        import *
from common._AltirocCalPulse    import *
from common._AltirocProbe       import *
from common._AltirocReadout     import *
from common._AltirocSlowControl import *
from common._AltirocTdcClk      import *
from common._AltirocTrig        import *
from common._Dac                import *
from common._DataStreamReader   import *
from common._Fpga               import *
from common._Top                import *

def getNsValue(var):
    return ( var.dependencies[0].value() + 1 )*6.25 
    
def getMhzValue(var):
    value = var.dependencies[0].value() + var.dependencies[1].value() + 2
    return 1/(value*0.00625)      
    