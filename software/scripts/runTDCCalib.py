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


    board=args.board
    NTOA=100#was 500
    NTOT=50
    totRiseEdgeMin=700
    totRiseEdgeMax=3000
    totRiseEdgeStep=20   #Need 1 for TOTf
    chList=list(range(0,15))
    #chList=[4,9,14]    
    toaDelayStep=1
    toaDelayMin=1900
    toaDelayMax=2350

    #HighStat
    #chList=[4,9,14]    
    #NTOA=500#was 500
    #toaDelayStep=20
    
    if board==2:
        toaDelayMin=1800
        toaDelayMax=2300
        #chList=[7,8,6,10,12,13,14,5]
    elif board==3:
        toaDelayMin=1900
        toaDelayMax=2300
        #chList=list(range(2,9))+list(range(10,15))+[1]
    elif board==8:
        toaDelayMin=1950
        toaDelayMax=2300
        #chList=[4,9,14]
    elif board==12:
        toaDelayMin=1850
        toaDelayMax=2350
    elif board==13:
        toaDelayMin=1850
        toaDelayMax=2300
    elif board==15:
        toaDelayMin=1900
        toaDelayMax=2350
    elif board==18:
        toaDelayMin=1900
        toaDelayMax=2350
        #chList=[0,1,2,3,5,9,10,11,12,13,14]


    for ch in chList:
        if args.toa:
            #nameTOA='Data/delayScanTrigExt_B_%d_ch_%d_'%(board,ch)
            nameTOA='Data/delayScanTrigExt_'
            cmdTOA="python scripts/measureTOA.py --skipExistingFile True -N %s --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --ch %d --Cd 0 --useExt True --delayMin %d --delayMax %d --delayStep %d  --out %s"%(NTOA,board,ch,toaDelayMin,toaDelayMax,toaDelayStep,nameTOA)
            print(cmdTOA)
            print("sleep 5")


        if args.tot:
            #nameTOT='Data/widthScanTrigExt_B_%d_ch_%d_'%(board,ch)
            nameTOT='Data/widthScanTrigExt_'
            cmdTOT="python scripts/measureTOT.py --skipExistingFile True  -N %s --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --ch %d --Cd 0 --useExt True --riseEdgeMin %d --riseEdgeMax %d --riseEdgeStep %s --out %s"%(NTOT,board,ch,totRiseEdgeMin,totRiseEdgeMax,totRiseEdgeStep,nameTOT)
            print(cmdTOT)
            print("sleep 5")

