# atlas-altiroc-daq

<!--- ########################################################################################### -->

# Before you clone the GIT repository

1) Setup for large filesystems on github (one-time step)

```
$ git lfs install
```

2) Verify that you have git version 2.9.0 (or later) installed 

```
$ git version
git version 2.9.0
```

3) Verify that you have git-lfs version 2.1.1 (or later) installed 

```
$ git-lfs version
git-lfs/2.1.1
```

<!--- ########################################################################################### -->

# Clone the GIT repository

```
$ git clone --recursive https://github.com/slaclab/atlas-altiroc-daq
```

<!--- ########################################################################################### -->

# How to build the firmware 

1) Setup your Xilinx Vivado:

> If you are on the SLAC AFS network:

```
$ source atlas-altiroc-daq/firmware/setup_env_slac.sh
```

> Else you will need to install Vivado and install the Xilinx Licensing

2) Go to the firmware's target directory:

```
$ cd atlas-altiroc-daq/firmware/targets/AtlasAltirocFpga1GbE
```

3) Build the firmware

```
$ make
```

4) Optional: Open up the project in GUI mode to view the firmware build results

```
$ make gui
```

Note: For more information about the firmware build system, please refer to this presentation:

> https://docs.google.com/presentation/d/1kvzXiByE8WISo40Xd573DdR7dQU4BpDQGwEgNyeJjTI/edit?usp=sharing

<!--- ########################################################################################### -->

# How to install the Rogue With Anaconda

> https://github.com/slaclab/rogue/blob/master/README_anaconda.md

<!--- ########################################################################################### -->

# How to run the Software Development GUI

```
# Go to software directory
$ cd atlas-altiroc-daq/software

# Activate Rogue conda Environment 
$ source /path/to/my/anaconda3/etc/profile.d/conda.sh

# Setup the Python Environment
$ source setup_env.sh

# Launch the GUI
$ python3 scripts/DevGui.py --ip <DHCP_IP_ADDRESS>
 
```

<!--- ########################################################################################### -->


# How to Reprogram the FPGA Firmware

```
# Go to software directory
$ cd atlas-altiroc-daq/software

# Activate Rogue conda Environment 
$ source /path/to/my/anaconda3/etc/profile.d/conda.sh

# Setup the Python Environment
$ source setup_env.sh

# Reprogram the FPGA
$ python3 scripts/ReprogramFpga.py --ip <DHCP_IP_ADDRESS> --mcs <PATH_TO_MCS_FILE>
```

<!--- ########################################################################################### -->

# How to Reprogram the SiLab PLL's NVM

```
# Go to software directory
$ cd atlas-altiroc-daq/software

# Activate Rogue conda Environment 
$ source /path/to/my/anaconda3/etc/profile.d/conda.sh

# Setup the Python Environment
$ source setup_env.sh

# Update the PLL"s NVM (configuration sotred in config/pll-config/Si5345-RevD-Registers.csv)
$ python3 scripts/BurnPllNvm.py --ip <DHCP_IP_ADDRESS>
```

<!--- ########################################################################################### -->
