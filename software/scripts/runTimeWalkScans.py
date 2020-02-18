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
    #parser.add_argument("--vthc64", type = argBool, required = False, default = False)
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
    chList=None
    dacList=None
    f=open("runTW_B"+str(board)+".sh","w")

    
    doTOA=0
    doTW=1
    doThres=0
    

    dacList=getDACList(board)
    dacRef=min(dacList.values())
    useVthc=False
    
    if board==8:
        cdList=[4];
        #cdList=[4];chList=[4,9,14];
        #chList=[4];cdList=[4];#TDR
        #cdList=[4];
        #chList=[14]
        #cdList=range(0,8);chList=[4]#,9,14];
        #cdList=[0];dacList=range(290,390,10);chList=list(range(0,15));qStep=2;
        #chList=list(range(0,25))
        delayList=[2500]
    elif board==13:
        #chList=[0,4,5,10]
        chList=[0]
        pass
    elif board==15:
        chList=[4,9,14,19,24]
        #chList=range(15)
        cdList=[0,4]
        pass


    if chList==None:
        if dacList==None or len(dacList)==0:
            chList=range(15)
        else:            
            chList=sorted(dacList.keys())
        #chList=list(range(15,25))+list(range(0,15))


    ###############################
    # TW and TOA
    ###############################
    for ch in chList:
        for cd in cdList:            
            #dac list
            if useVthc:
                dacNom=dacRef
            else:
                dacNom=dacList[ch]
            dacListLocal=[dacNom]
            #dacListLocal=list(range(dacNom-20,dacNom+200,2));qMin=5;qMax=41;qStep=5 #for pulse shape
            dacListLocal=list(range(dacNom-20,dacNom+300,5));qMin=5;qMax=41;qStep=5 #for pulse shape
            #dacListLocal=list(range(dacNom+300,1000,20));qMin=5;qMax=41;qStep=5 #for pulse shape
            
            
            print(ch,cd,delayList,dacListLocal)            
            for dac in dacListLocal:   

                ###############################
                # measure TW
                ###############################
                for delay in delayList:
                    name="Data/"
                    cmd="python scripts/measureTimeWalk.py --skipExistingFile True --moreStatAtLowQ False --morePointsAtLowQ True --debug False --display False -N %d --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board %d  --delay %d  --QMin %d --QMax %d --QStep %d --out %s  --ch %d  --Cd %d --DAC %d --Rin_Vpa %d"%(N,board,delay,qMin,qMax,qStep,name,ch,cd,dac,Rin_Vpa)
                    if not useVthc:
                        cmd+=" --Vthc 64"
                        pass
                    if args.cfg is not None:
                        cmd+=" --cfg "+args.cfg
                        pass
                        
                    if doTW: f.write(cmd+"\n sleep 5 \n")
                    
                ###############################
                # measure TOA
                ###############################

                QList=list(range(3,10,1))+[13,21]
                #QList=list(range(3,10,1))+list(range(10,27,4)):
                QList=[5,13,26]
                for Q in QList:
                    delayMin=2200
                    delayMax=2700
                    if Q<0:                        
                        delayMin=1800
                        delayMax=2300
                    logName='Data/delayTOA_B_%d_rin_%d_ch_%d_cd_%d_Q_%d_thres_%d.log'%(board,Rin_Vpa,ch,cd,Q,dac)
                    cmd="python scripts/measureTOA.py --skipExistingFile True -N 100 --debug False --display False --Cd %d --checkOFtoa False --checkOFtot False --ch %d --board %d --DAC %d --Q %d --delayMin %d --delayMax %d --delayStep 5 --out Data/delay "%(cd,ch,board,dac,Q,delayMin,delayMax)
                    if not useVthc:
                        cmd+=" --Vthc 64"
                        pass
                    if Q<0:
                        cmd+=" --useExt True "
                    cmd+=" >& "+logName
                    if doTOA:f.write(cmd+"\n sleep 5 \n")





    ###############################
    # thres. scan
    ###############################        
    if doThres:
        for ch in chList:
            for cd in cdList:
                #QList=range(0,63,10)
                QList=[0]#,10,20]
                #QList=[4]
                for Q in QList:#ATT TRIG EXT
                    thresMin=260
                    thresMax=1200
                    thresStep=5
                    if Q >=5:thresMin=dacList[ch]-10
                    thresStep=1
                    N=100
                    cmd="python scripts/thresholdScan.py  --skipExistingFile True --N %d --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --delay %d --minVth %d --maxVth %d --VthStep %d --Cd %d --ch %d --Q %d --out Data/ --autoStop True"%(N,board,delayList[0],thresMin,thresMax,thresStep,cd,ch,Q)
                    if not useVthc:
                        cmd+=" --Vthc 64"
                        pass
                    f.write(cmd+"\n sleep 5 \n")


                    
                    


print (" ************ CHECK TRIG EXT ***************")
