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
    parser.add_argument("-b", "--board", type = int, required = False, default = 8,help = "Choose board")
    parser.add_argument("-c","--ch", type = int, required = False, default = 4, help = "channel")
    parser.add_argument("--useVthc", type = bool, required = False, default = False)
    # Get the arguments
    args = parser.parse_args()
    return args




if __name__ == "__main__":
    args = parse_arguments()


    cdList=[0]
    qMin=2
    qMax=26#63#63
    qStep=1
    board=args.board
    N=100
    Rin_Vpa=0
    delayList=[2450]
    #delayList=range(2450,2550+1,20) 
    chList=None
    dacList=None

    f=open("runTW_B"+str(board)+".sh","w")
    
    if board==2:
        #####chList=[5,6,7,8,10,12,13,14]#list(range(15,25))+
        #chList=[14]#list(range(15,25))+
        #dacList=range(300,440,10)
        dacRef={}
        dacRef[5]=350
        dacRef[6]=360
        dacRef[7]=350
        dacRef[8]=330
        dacRef[10]=380
        dacRef[12]=320
        dacRef[13]=340
        dacRef[14]=330
    elif board==3:
        #chList=list(range(1,9))+list(range(10,15))
        #dacList=range(300,380,10)
        dacRef={}
        dacRef[1]=408
        dacRef[2]=310
        dacRef[3]=348
        dacRef[4]=334
        dacRef[5]=374
        dacRef[6]=362
        dacRef[7]=344
        dacRef[8]=356      
        dacRef[10]=340
        dacRef[11]=374
        dacRef[12]=360
        dacRef[13]=382
        dacRef[14]=418        
    elif board==8:
        qMin=1
        #cdList=[4];chList=[4,9,14];
        #cdList=range(0,8);chList=[4]#,9,14];
        #cdList=[0];dacList=range(290,390,10);chList=list(range(0,15));qStep=2;
        #chList=list(range(0,25))
        delayList=[2500]
        dacRef={}
        dacRef[0]=   350 
        dacRef[1]=   340  
        dacRef[2]=   300
        dacRef[3]=   350
        dacRef[4]=   350
        dacRef[5]=   350
        dacRef[6]=   340#TOAfrac=0.2
        dacRef[7]=   310#TOAfrac=0.2
        dacRef[8]=   340
        dacRef[9]=   300 
        dacRef[10]=  370
        dacRef[11]=  360
        dacRef[12]=  340 
        dacRef[13]=  380
        dacRef[14]=  320#cd4310 cd 0 320



    elif board==13:
        #chList=list(range(0,6))+list(range(7,15))
        #chList=[7,12,21]
        #dacList=range(300,440,10)
        dacRef={}
        dacRef[0]=330
        dacRef[1]=310
        dacRef[2]=340
        dacRef[3]=330
        dacRef[4]=320
        dacRef[5]=400
        dacRef[7]=320
        dacRef[8]=350      
        dacRef[9]=340  
        dacRef[10]=330
        dacRef[11]=350
        dacRef[12]=370
        dacRef[13]=360
        dacRef[14]=360
        dacRef[15]=300
        dacRef[16]=380
        dacRef[17]=330
        dacRef[18]=390
        dacRef[19]=370      
        dacRef[20]=350
        dacRef[21]=340
        dacRef[22]=430
        dacRef[23]=400
        dacRef[24]=360
    elif board==15:
        chList=[4,9,14,19,24]
        cdList=[0,4]
        dacList=range(300,410,10)
        dacRef={}
        dacRef[0]=330
        dacRef[1]=310
        dacRef[2]=340
        dacRef[3]=330
        dacRef[4]=320
        dacRef[5]=400
        dacRef[7]=320
        dacRef[8]=350      
        dacRef[9]=340  
        dacRef[10]=330
        dacRef[11]=350
        dacRef[12]=370
        dacRef[13]=360
        dacRef[14]=360
        dacRef[15]=300
        dacRef[16]=380
        dacRef[17]=330
        dacRef[18]=390
        dacRef[19]=370      
        dacRef[20]=350
        dacRef[21]=340
        dacRef[22]=430
        dacRef[23]=400
        dacRef[24]=360        
    elif board==18:
        dacRef={}
        dacRef[0]=360
        dacRef[1]=390
        dacRef[2]=406
        dacRef[3]=340
        #dacRef[4]=440
        dacRef[5]=360
        #dacRef[6]=
        #dacRef[7]=
        #dacRef[8]=      
        dacRef[9]=356  
        dacRef[10]=344
        dacRef[11]=336
        dacRef[12]=326
        dacRef[13]=376
        dacRef[14]=376

    dacCor={}
    dacRefNew={}
    if args.useVthc:
       meanDac=np.mean(dacRef.values())
       for ch in dacRef.keys():
           dacCor[ch]=int(64+(meanDac-dacRef[ch])*(0.4/0.8))
           dacRefNew[ch]=int(meanDac)
       dacRef=dacRefNew


    if chList==None:
        chList=dacRef.keys()
        #chList=list(range(15,25))+list(range(0,15))

        
    for ch in chList:
        for cd in cdList:
            if dacList is not None:
                dacListLocal=dacList
            else:
                #dac list
                dac=dacRef[ch]        
                #dacListLocal=list(range(dac,dac+41,8))
                #dacListLocal=list(range(dac-20,dac+21,10))
                #dacListLocal=list(range(dac-8,dac+1,2))
                dacListLocal=list(range(dac-10,dac+11,10))
                dacListLocal=[dac]
                #dacList=range(300,420,10)
                #print("============",ch,dacListLocal,dac)

            print(ch,cd,delayList,dacListLocal)
            
            for dac in dacListLocal:   

                #for Q in range(4,20,1):
                #for Q in list(range(3,13,1))+list(range(13,27,2)):
                #for Q in [5,8]:#,8,10,14,16,18,20,22]:
                for Q in [5,7,26]:#5,26]:#,8,10,14,16,18,20,22]:
                #for Q in [8,11]:#,8,10,14,16,18,20,22]:
                    delayMin=2200
                    delayMax=2700
                    # if board==8:
                    #     delayMin=2350
                    #     delayMax=2700
                        
                    cmd="python scripts/measureTOA.py --skipExistingFile True -N 100 --debug False --display False --Cd %d --checkOFtoa False --checkOFtot False --ch %d --board %d --DAC %d --Q %d --delayMin %d --delayMax %d --delayStep 1 --out Data/delay"%(cd,ch,board,dac,Q,delayMin,delayMax)
                    f.write(cmd+"\n sleep 5 \n")

                
                for delay in delayList:
                    #name='Data/thresscan_B_%d_rin_%d_ch_%d_cd_%d_delay_%d_thres_%d_'%(board,Rin_Vpa,ch,cd,delay,dac)
                    name="Data/thresscan"
                    if args.useVthc:
                       name+='corr_%d_' %dacCor[ch]
                    cmd="python scripts/measureTimeWalk.py --skipExistingFile True --morePointsAtLowQ False --debug False --display False -N %d --useProbePA False --useProbeDiscri False  --checkOFtoa False --checkOFtot False --board %d  --delay %d  --QMin %d --QMax %d --QStep %d --out %s  --ch %d  --Cd %d --DAC %d --Rin_Vpa %d"%(N,board,delay,qMin,qMax,qStep,name,ch,cd,dac,Rin_Vpa)
                    if args.useVthc:
                       cmd+=" --Vthc %d" %dacCor[ch]
                    #f.write(cmd+"\n sleep 5 \n")



            
