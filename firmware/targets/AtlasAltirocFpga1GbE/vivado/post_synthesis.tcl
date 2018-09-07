##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

##############################
# Get variables and procedures
##############################
source -quiet $::env(RUCKUS_DIR)/vivado_env_var.tcl
source -quiet $::env(RUCKUS_DIR)/vivado_proc.tcl

# Bypass the debug chipscope generation
return

############################
## Open the synthesis design
############################
open_run synth_1

###############################
## Set the name of the ILA core
###############################
set ilaName u_ila_0

##################
## Create the core
##################
CreateDebugCore ${ilaName}

#######################
## Set the record depth
#######################
set_property C_DATA_DEPTH 1024 [get_debug_cores ${ilaName}]

#################################
## Set the clock for the ILA core
#################################
SetDebugCoreClk ${ilaName} {U_Core/clk160MHz}

#######################
## Set the debug Probes
#######################

ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/afull[*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/data[0][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/data[1][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/data[2][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/data[3][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/enable[*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/header[0][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/header[1][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/header[2][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/header[3][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/invData[*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rdEn[*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxData[0][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxData[1][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxData[2][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxData[3][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxHeader[0][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxHeader[1][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxHeader[2][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxHeader[3][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxStatus[0][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxStatus[1][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxStatus[2][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxStatus[3][*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rxValid[*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/valid[*]}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/chBond}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rst160MHz}
ConfigProbe ${ilaName} {U_Core/GEN_VEC[0].U_RxPhy/U_RxPhy/U_RxPhyLayer/rst160MHzL}

##########################
## Write the port map file
##########################
WriteDebugProbes ${ilaName} 
