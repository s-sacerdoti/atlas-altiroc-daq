# Load RUCKUS environment and library
source -quiet $::env(RUCKUS_DIR)/vivado_proc.tcl

# Load common and sub-module ruckus.tcl files
loadRuckusTcl $::env(PROJ_DIR)/../../submodules/surf
loadRuckusTcl $::env(PROJ_DIR)/../../common/

# Load local source Code
loadSource      -dir  "$::DIR_PATH/hdl"
loadConstraints -dir  "$::DIR_PATH/hdl"
set_property top {AtlasAltirocFpga1GbE}   [get_filesets sources_1]

# Load local SIM source Code
loadSource -sim_only -dir  "$::DIR_PATH/tb"
set_property top {AtlasAltirocFpga1GbETb} [get_filesets sim_1]

