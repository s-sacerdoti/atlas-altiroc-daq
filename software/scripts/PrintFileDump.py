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

import pyrogue as pr
import rogue.utilities.fileio
import numpy as np

import common as feb

import argparse
import sys
import os

#################################################################

# Set the argument parser
parser = argparse.ArgumentParser()

# Add arguments
parser.add_argument(
    "--dataFile", 
    type     = str,
    required = True,
    help     = "path to data file",
) 

# Get the arguments
args = parser.parse_args()

#################################################################

# Create the File reader streaming interface
dataReader = rogue.utilities.fileio.StreamReader()

# Create the Event reader streaming interface
dataStream = feb.PrintEventReader(cvsDump=True)

# Connect the file reader ---> event reader
pr.streamConnect(dataReader, dataStream) 

# Open the file
dataReader.open(args.dataFile)

# Close file once everything processed
dataReader.closeWait()
