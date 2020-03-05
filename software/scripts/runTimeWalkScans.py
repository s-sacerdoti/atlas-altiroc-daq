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

#####################
# 
#####################
doThres= 0
doTW   = 0
doNoise= 0
doTOA  = 0
doPS   = 1 # TW with thres. scan

useVthcFromConfig=False
chList=None
#chList=[4,9,14]

#####################
# TW
#####################
qMin=1
qMax=63#63#63
qStep=1
Ntw=100
if doPS:
    doTW=1

    
#####################
# TOA
#####################
#Ntoa=500;delayStep=20 #Default to check distributions
Ntoa=100;delayStep=5  #to measure jitter
#Ntoa=100; delayStep=1  #TDR
QTOAList=[4,5,6,7,8,9,13,26,52]#default
QTOAList=[5,6,13,52]#default
#QTOAList=list(range(3,10,1))+[13,21]#jitter vs Q



#####################
# Threshold
#####################
Nthres=100
QThresList=[4]#default
thresMin=260  #overwritten for Q>5
thresMax=1023#max is 1023
thresStep=2
if doNoise:
    Nthres=1000
    doThres= 1
    thresStep=1
    #thresMin= #
    thresMax=1000
    QThresList=[0,6,13]


    
def parse_arguments():
    parser = argparse.ArgumentParser()
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    parser.add_argument("-b", "--board", type = int, required = False, default = 8,help = "Choose board")
    parser.add_argument("-c","--ch", type = int, required = False, default = 4, help = "channel")
    parser.add_argument("--cfg", required = False, default = None)
    args = parser.parse_args()
    return args



if __name__ == "__main__":
    args = parse_arguments()
    board=args.board

    fname="runTW_B"+str(board)+".sh"
    f=open(fname,"w")

    Rin_Vpa=0
    delay=2450
    cdList=[0]
    dacMap=None
    dacMap=getDACList(board)
    ###dacRef=0
    ###if len(dacMap.values())>0:
    ###    dacRef=min(dacMap.values())
    
    if board==8:
        cdList=[4];
        #cdList=[4];chList=[4,9,14];
        #chList=[4];cdList=[4];dacMap[4]=345#TDR
        #chList=[4,9]
        #cdList=range(0,8,1)
        #cdList=[0,4,7]
        #cdList=[5,6,3,2,1]
        
        #cdList=range(0,8);chList=[4]#,9,14];
        #cdList=[0];dacMap=range(290,390,10);chList=list(range(0,15));qStep=2;
        #chList=list(range(0,25))
        delay=2500
    elif board==12:
        cdList=[4];
    elif board==13:
        #chList=[11,12,13,14]
        #chList=[0]
        #chList=[4,9,1,0,14]
        #chList=[14]
        pass
    elif board==15:
        chList=[4,9,14,19,24]
        #chList=range(15)
        cdList=[0,4]
        pass


    if chList==None:
        if dacMap==None or len(dacMap)==0:
            chList=range(15)
        else:            
            chList= set([k[0] for k in sorted(dacMap.keys())])
        #chList=list(range(15,25))+list(range(0,15))


    ###############################
    # TW and TOA
    ###############################
    for ch in chList:
        for cd in cdList:            
            #dac list
            dacNom=0
            if useVthcFromConfig:
                dacNom=0###dacRef
                vthcList=[-1]
            else:
                vthcList=[64]
                if (ch,cd) in dacMap.keys():
                    dacNom=dacMap[(ch,cd)]
                else:
                    print ("PRB with dacMap, break")
                    break
            dacListLocal=[dacNom]

            
            if doPS:
                qMin=0;
                qMax=26;
                qStep=4 #for pulse shape#PULSESHAPE    
                dacListLocal=list(range(dacNom-40,dacNom+100,4))+list(range(dacNom+100,dacNom+200,4));
            
            print(ch,cd,delay,dacListLocal,vthcList)            
            for dac in dacListLocal:   

                ###############################
                # measure TW
                ###############################
                for vthc in vthcList:
                    name="Data/"
                    cmd="python scripts/measureTimeWalk.py --skipExistingFile True --moreStatAtLowQ False --morePointsAtLowQ True --debug False --display False -N %d --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board %d  --delay %d  --QMin %d --QMax %d --QStep %d --out %s  --ch %d  --Cd %d --DAC %d --Rin_Vpa %d"%(Ntw,board,delay,qMin,qMax,qStep,name,ch,cd,dac,Rin_Vpa)

                    
                    if not useVthcFromConfig:#take the one from config
                        #vthc=64
                        cmd+=" --Vthc "+str(vthc)
                        pass
                    if args.cfg is not None:
                        cmd+=" --cfg "+args.cfg
                        pass
                        
                    if doTW: f.write(cmd+"\n sleep 5 \n")
                    
                ###############################
                # measure TOA
                ###############################

                for Q in QTOAList:
                    delayMin=2200#200
                    delayMax=2700
                    if Q<0:                        
                        delayMin=1800
                        delayMax=2300
                    logName='Data/delayTOA_B_%d_rin_%d_ch_%d_cd_%d_Q_%d_thres_%d.log'%(board,Rin_Vpa,ch,cd,Q,dac)
                    cmd="python scripts/measureTOA.py --skipExistingFile True -N %d --debug False --display False --Cd %d --checkOFtoa False --checkOFtot False --ch %d --board %d --DAC %d --Q %d --delayMin %d --delayMax %d --delayStep %d --out Data/delay "%(Ntoa,cd,ch,board,dac,Q,delayMin,delayMax,delayStep)
                    if not useVthcFromConfig:#take the one from config
                        #vthc=64
                        cmd+=" --Vthc "+str(vthc)
                        pass
                    if Q<0:
                        cmd+=" --useExt True "
                    #cmd+=" >& "+logName
                    if doTOA:f.write(cmd+"\n sleep 5 \n")





    ###############################
    # thres. scan
    ###############################        
    if doThres:
        for ch in chList:
            for cd in cdList:
                for Q in QThresList:#ATT TRIG EXT
                    if Q >5:thresMinLocal=dacMap[(ch,cd)]-10+(Q-4)*7
                    else:thresMinLocal=thresMin
                    cmd="python scripts/thresholdScan.py  --skipExistingFile True --N %d --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --delay %d --minVth %d --maxVth %d --VthStep %d --Cd %d --ch %d --Q %d --out Data/ --autoStop True"%(Nthres,board,delay,thresMinLocal,thresMax,thresStep,cd,ch,Q)
                    cmd+=" --Vthc 64"

                    f.write(cmd+"\n sleep 5 \n")


                    
                    
print (" ") 
print ("useVthcFromConfig:",useVthcFromConfig)
print (" " )
print (" ************ CHECK TRIG EXT ***************")
print("source "+fname)
