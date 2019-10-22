#!/bin/bash
##############################################################################
## This file is part of 'ATLAS ALTIROC DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS ALTIROC DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

# Setup environment
source /afs/slac.stanford.edu/g/reseng/vol26/anaconda/miniconda3/etc/profile.d/conda.sh

echo "Removing existing rogue_3.7.0 environment"
conda env remove -n rogue_3.7.0

echo "Creating new rogue_3.7.0 environment"
conda create -n rogue_3.7.0 -c defaults -c conda-forge -c paulscherrerinstitute -c tidair-tag rogue=v3.7.0

echo "Installing matplotlib"
pip install matplotlib
