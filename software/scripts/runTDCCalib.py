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




#################################################################
# 
#################################################################
def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    # Add arguments
    parser.add_argument("-b", "--board", type = int, required = False, default = 2,help = "Choose board")
    parser.add_argument("--toa", action="store_true", default = False)
    parser.add_argument("--tot", action="store_true", default = False)

    # Get the arguments
    args = parser.parse_args()
    return args




if __name__ == "__main__":
    args = parse_arguments()


    qMin=3
    qMax=63
    qStep=1
    board=args.board
    NTOA=100
    NTOT=100
    totDelayMin=700
    totDelayMax=3000
    totDelayStep=1   #Need 1 for TOTf
    
    if board==8:
        toaDelayMin=1900
        toaDelayMax=2300
        chList=[4,9,14]
    elif board==2:
        toaDelayMin=1800
        toaDelayMax=2300
        chList=[7,8,6,10,12,13,14,5]
    elif board==3:
        toaDelayMin=1800
        toaDelayMax=2300
        chList=list(range(2,9))+list(range(10,15))+[1]
    elif board==13:
        toaDelayMin=1850
        toaDelayMax=2350
        chList=list(range(0,25))
    elif board==18:
        toaDelayMin=1900
        toaDelayMax=2350
        chList=[0,1,2,3,5,9,10,11,12,13,14]
    

    for ch in chList:
        if args.toa:
            nameTOA='Data/delayScanTrigExt_B_%d_ch_%d_'%(board,ch)
            cmdTOA="python scripts/measureTOA.py -N %s --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --ch %d --useExt True --delayMin %d --delayMax %d --delayStep 1  --out %s"%(NTOA,board,ch,toaDelayMin,toaDelayMax,nameTOA)
            print(cmdTOA)
            print("sleep 5")


        if args.tot:
            nameTOT='Data/widthScanTrigExt_B_%d_ch_%d_'%(board,ch)
            cmdTOT="python scripts/measureTOT.py -N %s --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --ch %d --useExt True --pulserMin %d --pulserMax %d --pulserStep %s --out %s"%(NTOT,board,ch,totDelayMin,totDelayMax,totDelayStep,nameTOT)
            print(cmdTOT)
            print("sleep 5")

