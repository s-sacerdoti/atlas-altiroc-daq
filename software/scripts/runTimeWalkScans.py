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
from computeVth import *

#####################
# 
#####################


doThres= 1

doLinearity= 0 

doTW   = 0
doTOA  = 0

doPS   = 0 # TW with thres. scan
doXtalk= 0 # TOA Channels should be ON


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
Ntoa=100;
delayStep=5 
delayMin=2200
delayMax=2700
QTOAList=[4,5,6,7,8,9,13,26,52]#default
#QTOAList=[52]#ClockTree
#Ntoa=500;delayStep=20;#QTOAList=[52] #Default to check distributions

if doXtalk == 1:
    doTOA=1
    QTOAList=[13,60]
    args.useVthc=True
    delayMin=2400#200
    delayMax=2500
    delayStep=10
    Ntoa=200
    
#####################
# Threshold
#####################
Nthres=100
QThresList=[3]#default
thresMin=260  #overwritten for Q>5
thresMax=1023#max is 1023
thresStep=2
if doLinearity:
    Nthres=1000
    doThres= 1
    thresStep=1
    #thresMin= #
    thresMax=1000
    QThresList=[0,3,6,13,26,39,52]


    
def parse_arguments():
    parser = argparse.ArgumentParser()
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    parser.add_argument("-b", "--board", type = int, required = False, default = 8,help = "Choose board")
    parser.add_argument("-c","--ch", type = int, required = False, default = 4, help = "channel")
    parser.add_argument("--cfg", required = False, default = None)
    parser.add_argument("--chON", action="store_true", default = False)
    parser.add_argument("--ctestON", action="store_true", default = False)
    parser.add_argument("--useVthc", action="store_true", default = False)
    args = parser.parse_args()
    return args



if __name__ == "__main__":
    args = parse_arguments()
    

    boardASICAlone=[8,9,10,11,12,14,15]
    board=args.board

    fname="runTW_B"+str(board)
    if args.useVthc:
        fname+="_useVthc"
    if args.chON:
        fname+="_chON"
    if args.ctestON:
        fname+="_ctestON"
    f=open(fname+".sh","w")



    #detector capacitance
    cdList=[0]
    if board in boardASICAlone:
        cdList=[4,];
        #chList=[4,9]
        #cdList=[4,5,6,7];
        
    #threshold
    dacMap=None
    dacMap=getDACList(board)
    dacRef=0

    #channel list
    if chList==None:
        if dacMap==None or len(dacMap)==0:
            chList=range(15)
        else:            
            chList= set([k[1] for k in sorted(dacMap.keys())])
        #chList=list(range(15,25))+list(range(0,15))



        
    #special settings
    Rin_Vpa=0
    delay=2450
    if board==8:
        delay=2500


        
    ###############################
    # TW and TOA
    ###############################
    for ch in chList:
        for cd in cdList:            
            #dac list
            dacNom=0
            if args.useVthc:                
                dacRef,vthcMap=getVthc(board,cd)
                dacNom=dacRef
                vthcList=[-1]
            else:
                vthcList=[64]
                if (board,ch,cd) in dacMap.keys():
                    dacNom=dacMap[(board,ch,cd)]
                else:
                    print ("PRB with dacMap, break")
                    break
            dacListLocal=[dacNom]

            
            if doPS:
                qMin=0;
                qMax=26;
                qStep=4 #for pulse shape#PULSESHAPE
                dacListLocal=list(range(dacNom-40,dacNom+150,4))####+list(range(dacNom+100,dacNom+200,4));
            
            print(ch,cd,delay,dacListLocal,vthcList)            
            for dac in dacListLocal:   

                ###############################
                # measure TW
                ###############################
                for vthc in vthcList:
                    name="Data/"
                    cmd="python scripts/measureTimeWalk.py --skipExistingFile True --moreStatAtLowQ False --morePointsAtLowQ True --debug False --display False -N %d --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board %d  --delay %d  --QMin %d --QMax %d --QStep %d --out %s  --ch %d  --Cd %d --DAC %d --Rin_Vpa %d"%(Ntw,board,delay,qMin,qMax,qStep,name,ch,cd,dac,Rin_Vpa)

                    
                    if not args.useVthc:#take the one from config
                        #vthc=64
                        cmd+=" --Vthc "+str(vthc)
                        pass
                    if args.chON:
                        cmd+=" --allChON True"
                        pass
                    if args.ctestON:
                        cmd+=" --allCtestON True"
                        pass

                    if args.cfg is not None:
                        cmd+=" --cfg "+args.cfg
                        pass
                        
                    if doTW: f.write(cmd+"\n sleep 5 \n")
                    
                ###############################
                # measure TOA
                ###############################
                if dac!=dacNom: continue
                for Q in QTOAList:
                    if Q<0:#trig ext                        
                        delayMin=1800
                        delayMax=2300
                    logName='Data/delayTOA_B_%d_rin_%d_ch_%d_cd_%d_Q_%d_thres_%d.log'%(board,Rin_Vpa,ch,cd,Q,dac)
                    cmd="python scripts/measureTOA.py --skipExistingFile True -N %d --debug False --display False --Cd %d --checkOFtoa False --checkOFtot False --ch %d --board %d --DAC %d --Q %d --delayMin %d --delayMax %d --delayStep %d --out Data/delay "%(Ntoa,cd,ch,board,dac,Q,delayMin,delayMax,delayStep)

                    if not args.useVthc:#take the one from config
                        #vthc=64
                        cmd+=" --Vthc "+str(vthc)
                        pass
                    if args.chON:
                        cmd+=" --allChON True"
                        pass
                    if args.ctestON:
                        cmd+=" --allCtestON True"
                        pass
                    if Q<0:
                        cmd+=" --useExt True "
                    if doXtalk:
                        cmd+=" --readAllChannels True  --allChON True "
                        cmd+=" >& "+logName
                    if doTOA:f.write(cmd+"\n sleep 5 \n")





    ###############################
    # thres. scan
    ###############################        
    if doThres:
        for ch in chList:
            for cd in cdList:
                for Q in QThresList:#ATT TRIG EXT
                    if Q >5:thresMinLocal=dacMap[(board,ch,cd)]-20+(Q-3)*7
                    else:thresMinLocal=thresMin
                    cmd="python scripts/thresholdScan.py  --skipExistingFile True --N %d --debug False --display False --checkOFtoa False --checkOFtot False  --board %d --delay %d --minVth %d --maxVth %d --VthStep %d --Cd %d --ch %d --out Data/ --autoStop True  --Q %d "%(Nthres,board,delay,thresMinLocal,thresMax,thresStep,cd,ch,Q)
                    cmd+=" --Vthc 64"

                    f.write(cmd+"\n sleep 5 \n")


                    
                    
print (" ") 
print ("args.useVthc:",args.useVthc)
print (" " )
print (" ************ CHECK TRIG EXT ***************")
print("source "+fname)
