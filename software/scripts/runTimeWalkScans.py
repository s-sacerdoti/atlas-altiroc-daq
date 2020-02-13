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

#################################################################
# 
#################################################################
def parse_arguments():
    parser = argparse.ArgumentParser()
    
    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    # Add arguments
    parser.add_argument("-b", "--board", type = int, required = False, default = 8,help = "Choose board")
    parser.add_argument("-c","--ch", type = int, required = False, default = 4, help = "channel")
    parser.add_argument("--vthc64", type = argBool, required = False, default = False)
    parser.add_argument("--cfg", required = False, default = None)
    #parser.add_argument("--dacRef", required = False, default = None)
    # Get the arguments
    args = parser.parse_args()
    return args




if __name__ == "__main__":
    args = parse_arguments()

    cdList=[0]
    qMin=1
    qMax=63#63#63
    qStep=2
    board=args.board
    N=100
    Rin_Vpa=0
    delayList=[2450]
    #delayList=range(2450,2550+1,20) 
    chList=None
    dacList=None

    doTOA=0
    doTW=0
    doThres=1
    dacList=getDACList(board)
    f=open("runTW_B"+str(board)+".sh","w")



    if board==8:
        qMin=1
        cdList=[4];
        #cdList=[4];chList=[4,9,14];
        #chList=[4];cdList=[4];#TDR
        #cdList=[4];
        #chList=[14]
        #cdList=range(0,8);chList=[4]#,9,14];
        #cdList=[0];dacList=range(290,390,10);chList=list(range(0,15));qStep=2;
        #chList=list(range(0,25))
        delayList=[2500]
    elif board==15:
        chList=[4,9,14,19,24]
        cdList=[0,4]
        pass


    if chList==None:
        chList=dacList.keys()
        #chList=list(range(15,25))+list(range(0,15))

        
    for ch in chList:
        for cd in cdList:
            
            ###############################
            # thres. scan
            ###############################
            for Q in [4]:#ATT TRIG EXT
                thresMin=270
                #thresMin=dacList[ch]-20
                thresMax=600
                thresStep=5
                cmd="python scripts/thresholdScan.py  --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --delay %d --minVth %d --maxVth %d --VthStep %d --Cd %d --ch %d --Q %d --out Data/ --autoStop True"%(board,delayList[0],thresMin,thresMax,thresStep,cd,ch,Q)
                if doThres:f.write(cmd+"\n sleep 5 \n")


            
            #dac list
            dac=dacList[ch]        
            #dacListLocal=list(range(dac,dac+41,8))
            #dacListLocal=list(range(dac-20,dac+21,10))
            #dacListLocal=list(range(dac-8,dac+1,2))
            #dacListLocal=list(range(dac-15,dac+1,5))
            dacListLocal=[dac]
            #dacListLocal=[dacRef]
            #dacListLocal=list(range(dacRef+20,dacRef+140,20))
            #dacListLocal=list(range(dacRef-20,dacRef+100,5))+list(range(dacRef+100,dacRef+400,10))#B8            
            print(ch,cd,delayList,dacListLocal)            
            for dac in dacListLocal:   

                ###############################
                # measure TW
                ###############################
                for delay in delayList:
                    #name='Data/thresscan_B_%d_rin_%d_ch_%d_cd_%d_delay_%d_thres_%d_'%(board,Rin_Vpa,ch,cd,delay,dac)
                    name="Data/thresscan"
                    name="Data/"
                    cmd="python scripts/measureTimeWalk.py --skipExistingFile True --moreStatAtLowQ False --morePointsAtLowQ False --debug False --display False -N %d --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board %d  --delay %d  --QMin %d --QMax %d --QStep %d --out %s  --ch %d  --Cd %d --DAC %d --Rin_Vpa %d"%(N,board,delay,qMin,qMax,qStep,name,ch,cd,dac,Rin_Vpa)
                    if args.vthc64:
                        cmd+=" --Vthc 64"
                        pass
                    if args.cfg is not None:
                        cmd+=" --cfg "+args.cfg
                        pass
                        
                    if doTW: f.write(cmd+"\n sleep 5 \n")
                    
                ###############################
                # measure TOA
                ###############################
                #for Q in range(3,22,1):
                #for Q in list(range(3,10,1))+list(range(10,27,4)):
                #for Q in [6,8]:#5,26]:#,8,10,14,16,18,20,22]:
                #for Q in [5,6,7,26]:#5,6,7]:#,8]#,26]:#5,26]:#,8,10,14,16,18,20,22]:
                for Q in [40]:#ATT TRIG EXT
                    delayMin=2200
                    delayMax=2700
                    if Q<0:                        
                        delayMin=1800
                        delayMax=2300
                    logName='Data/delayTOA_B_%d_rin_%d_ch_%d_cd_%d_Q_%d_thres_%d.log'%(board,Rin_Vpa,ch,cd,Q,dac)
                    cmd="python scripts/measureTOA.py --skipExistingFile True -N 100 --debug False --display False --Cd %d --checkOFtoa False --checkOFtot False --ch %d --board %d --DAC %d --Q %d --delayMin %d --delayMax %d --delayStep 5 --out Data/delay "%(cd,ch,board,dac,Q,delayMin,delayMax)
                    if Q<0:
                        cmd+=" --useExt True "
                    cmd+=" >& "+logName
                    if doTOA:f.write(cmd+"\n sleep 5 \n")







print (" ************ CHECK TRIG EXT ***************")
