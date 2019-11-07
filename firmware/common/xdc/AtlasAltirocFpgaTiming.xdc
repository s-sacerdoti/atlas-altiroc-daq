##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

create_clock -name gtClkP      -period 3.200 [get_ports { gtClkP }];      # 315.25 MHz

# create_clock -name localRefClk -period 6.237 [get_ports { localRefClkP }]; # 160.32 MHz (on-board reference)
# create_clock -name clk160MHz   -period 6.237 [get_ports { pllClkInP[0] }]; # 160.32 MHz (4 x 40.08 MHz LHC clock)
# Place/Route as 200 MHz to provide more timing margin (safety factor)
create_clock -name localRefClk -period 5.000 [get_ports { localRefClkP }]
create_clock -name clk160MHz   -period 5.000 [get_ports { pllClkInP[0] }]

create_generated_clock -name dnaClk    [get_pins {U_Core/U_System/U_AxiVersion/GEN_DEVICE_DNA.DeviceDna_1/GEN_7SERIES.DeviceDna7Series_Inst/BUFR_Inst/O}] 
create_generated_clock -name dnaClkInv [get_pins {U_Core/U_System/U_AxiVersion/GEN_DEVICE_DNA.DeviceDna_1/GEN_7SERIES.DeviceDna7Series_Inst/DNA_CLK_INV_BUFR/O}] 

set_clock_groups -asynchronous \ 
   -group [get_clocks -include_generated_clocks {gtClkP}] \
   -group [get_clocks -include_generated_clocks {localRefClk}] \
   -group [get_clocks -include_generated_clocks {clk160MHz}]
