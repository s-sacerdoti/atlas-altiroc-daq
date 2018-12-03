##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# Setup anaconda3 on the SLAC AFS network
source /u/re/ruckman/projects/WorkSpace/anaconda3/etc/profile.d/conda.csh

## Activate Rogue conda Environment 
conda activate rogue_env

# Python Package directories
setenv SURF_DIR ${PWD}/../firmware/submodules/surf/python

# Setup python path
setenv PYTHONPATH ${PWD}/python:${SURF_DIR}:${PYTHONPATH}
