##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

create_clock -name gtClkP      -period  3.200 [get_ports { gtClkP }];       # 315.25 MHz
create_clock -name localRefClk -period  6.250 [get_ports { localRefClkP }]; # 160 MHz    (on-board reference)
create_clock -name pllClkIn0   -period 24.950 [get_ports { pllClkInP[0] }]; #  40.08 MHz (1 x 40.08 MHz LHC clock)
# create_clock -name pllClkIn1   -period  3.118 [get_ports { pllClkInP[1] }]; # 320.64 MHz (8 x 40.08 MHz LHC clock)
create_clock -name pllClkIn1   -period 12.475 [get_ports { pllClkInP[1] }]; #  80.16 MHz (8 x 40.08 MHz LHC clock)
create_clock -name pllClkIn2   -period  3.118 [get_ports { pllClkInP[2] }]; # Undefined
create_clock -name pllClkIn3   -period  3.118 [get_ports { pllClkInP[3] }]; # Undefined

create_generated_clock -name iprogClk  [get_pins {U_Core/U_System/U_AxiVersion/GEN_ICAP.Iprog_1/GEN_7SERIES.Iprog7Series_Inst/DIVCLK_GEN.BUFR_ICPAPE2/O}] 
create_generated_clock -name dnaClk    [get_pins {U_Core/U_System/U_AxiVersion/GEN_DEVICE_DNA.DeviceDna_1/GEN_7SERIES.DeviceDna7Series_Inst/BUFR_Inst/O}] 
create_generated_clock -name dnaClkInv [get_pins {U_Core/U_System/U_AxiVersion/GEN_DEVICE_DNA.DeviceDna_1/GEN_7SERIES.DeviceDna7Series_Inst/DNA_CLK_INV_BUFR/O}] 
create_generated_clock -name clk160MHz [get_pins {U_Core/U_Clk/U_PLL/PllGen.U_Pll/CLKOUT0}]
create_generated_clock -name clk40MHz  [get_pins {U_Core/U_Clk/U_PLL/PllGen.U_Pll/CLKOUT1}]

set_clock_groups -asynchronous \ 
   -group [get_clocks -include_generated_clocks {gtClkP}] \
   -group [get_clocks -include_generated_clocks {localRefClk}] \
   -group [get_clocks -include_generated_clocks {pllClkIn0}] \
   -group [get_clocks -include_generated_clocks {pllClkIn1}] \
   -group [get_clocks -include_generated_clocks {pllClkIn2}] \
   -group [get_clocks -include_generated_clocks {pllClkIn3}]
