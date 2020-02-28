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
doTW   = 0
doPS   = 0 # TW with thres. scan
doTOA  = 0
doThres= 0
doNoise= 1 # can be only Noise or Line
doLin  = 0
useVthc=False
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
    doTOA=0
    doNoise=0
    doLin=0
    
#####################
# TOA
#####################
#Ntoa=500;delayStep=20 #Default to check distributions
Ntoa=100;delayStep=5  #to measure jitter
#Ntoa=100; delayStep=1  #TDR
QTOAList=[5,26,52]#default
#QTOAList=list(range(3,10,1))+[13,21]#jitter vs Q
#QTOAList=[4,5,6,7,8,9,10,11,12,13,26,52]#to measure jitter vs Q


#####################
# Threshold
#####################
Nthres=100
QThresList=[4]#default
thresMin=260  #overwritten for Q>5
thresMax=1023#max is 1023
thresStep=5
if doNoise:
    Nthres=1000
    doThres= 1
    thresStep=1
    #thresMin= #
    thresMax=400
    QThresList=[0]
elif doLin:
    Nthres=100
    doThres= 1
    thresStep=5
    QThresList=[10,20,30,40,50,60]
    
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
    dacList=None
    dacList=getDACList(board)
    dacRef=0
    if len(dacList.values())>0:
        dacRef=min(dacList.values())
    
    if board==8:
        cdList=[4];
        #cdList=[4];chList=[4,9,14];
        #chList=[4];cdList=[4];dacList[4]=345#TDR
        #chList=[4,9]
        #cdList=[4,5,6,7]
        cdList=[0,7,1,6,2,5,3];chList=[4]
        
        #cdList=[2,3,5,6];chList=[9]
        
        #cdList=range(0,8);chList=[4]#,9,14];
        #cdList=[0];dacList=range(290,390,10);chList=list(range(0,15));qStep=2;
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
                vthcList=[-1]
            else:
                vthcList=[64]
                if ch in dacList.keys():
                    dacNom=dacList[ch]
                else:
                    print ("PRB with dacList, break")
                    break
            dacListLocal=[dacNom]


            # dacListLocal=[]
            # if ch==4:
            #      if cd ==7: dacListLocal+=[350]
            #      if cd in [6]: dacListLocal+=[354]
            #      if cd in [5]: dacListLocal+=[358]
            #      if cd in [4]: dacListLocal+=[362]
            # if ch==9:
            #      if cd ==7: dacListLocal+=[296]
            #      if cd in [6]: dacListLocal+=[300]
            #      if cd in [5]: dacListLocal+=[304]
            #      if cd in [4]: dacListLocal+=[308]                
            # nom=dacListLocal[0]#ugly
            # dacListLocal=list(range(nom-40,nom+100,2))+list(range(nom+100,nom+200,4));qMin=5;qMax=22;qStep=4 #for pulse shape#PULSESHAPE
            #vthcList=list(range(63,0,-2));qMin=5;qMax=41;qStep=5 #for pulse shape
            if doPS:
                dacListLocal=list(range(dacNom-40,dacNom+100,2))+list(range(dacNom+100,dacNom+200,4));qMin=5;qMax=22;qStep=4 #for pulse shape#PULSESHAPE    
            
            print(ch,cd,delay,dacListLocal,vthcList)            
            for dac in dacListLocal:   

                ###############################
                # measure TW
                ###############################
                for vthc in vthcList:
                    name="Data/"
                    cmd="python scripts/measureTimeWalk.py --skipExistingFile True --moreStatAtLowQ False --morePointsAtLowQ True --debug False --display False -N %d --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board %d  --delay %d  --QMin %d --QMax %d --QStep %d --out %s  --ch %d  --Cd %d --DAC %d --Rin_Vpa %d"%(Ntw,board,delay,qMin,qMax,qStep,name,ch,cd,dac,Rin_Vpa)

                    
                    if not useVthc:#take the one from config
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
                    if not useVthc:#take the one from config
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
                    if Q >5:thresMinLocal=dacList[ch]-10+(Q-4)*7
                    else:thresMinLocal=thresMin
                    cmd="python scripts/thresholdScan.py  --skipExistingFile True --N %d --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --delay %d --minVth %d --maxVth %d --VthStep %d --Cd %d --ch %d --Q %d --out Data/ --autoStop True"%(Nthres,board,delay,thresMinLocal,thresMax,thresStep,cd,ch,Q)
                    cmd+=" --Vthc 64"

                    f.write(cmd+"\n sleep 5 \n")


                    
                    
print (" ") 
print ("useVthc:",useVthc)
print (" " )
print (" ************ CHECK TRIG EXT ***************")
print("source "+fname)
