# Load RUCKUS environment and library
source -quiet $::env(RUCKUS_DIR)/vivado_proc.tcl

# Load common and sub-module ruckus.tcl files
loadRuckusTcl $::env(PROJ_DIR)/../../submodules/surf
loadRuckusTcl $::env(PROJ_DIR)/../../common/

# Load target's source code
loadSource -sim_only -dir "$::DIR_PATH/tb"

# Set the top level synth_1 and sim_1
set_property top {AtlasAltirocCore}   [get_filesets sources_1]
set_property top {AtlasAltirocFpgaTb} [get_filesets sim_1]
