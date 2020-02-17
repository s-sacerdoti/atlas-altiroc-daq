#!/usr/bin/env python3

#################################################################
import sys                                                     ##
import time                                                    ##
import random                                                  ##
import argparse                                                ##
import pickle                                                  ##
import numpy as np                                             ##
import os                                                      ##
import math                                                    ##
#################################################################

from DAC import *


parser = argparse.ArgumentParser()
argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
parser.add_argument("-b", "--board", type = int, required = False, default = 13,help = "Choose board")
args = parser.parse_args()


dacList=getDACList(args.board)


dacRef=min(dacList.values())
print (dacRef)
i=0

print ("        DAC10bit: "+str(dacRef))
for i,d in dacList.items():

    vthc=int(64+(dacRef-d)*0.4/0.8)


    
    print ("        bit_vth_cor["+str(i)+"]: "+str(vthc))
