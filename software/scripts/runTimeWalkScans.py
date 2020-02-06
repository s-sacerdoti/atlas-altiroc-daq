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

    f=open("runTW_B"+str(board)+".sh","w")
    
    if board==2:
        #####chList=[5,6,7,8,10,12,13,14]#list(range(15,25))+
        chList=[10]#list(range(15,25))+
        #dacList=range(300,440,10)
        dacRef=320#Vthcor computed for this value
        dacList={}
        dacList[5]=350
        dacList[6]=360
        dacList[7]=350
        dacList[8]=330
        dacList[10]=380
        dacList[12]=320
        dacList[13]=340
        dacList[14]=330
    elif board==3:
        #chList=list(range(1,9))+list(range(10,15))
        #dacList=range(300,380,10)
        dacList={}
        dacList[1]=408
        dacList[2]=310
        dacList[3]=348
        dacList[4]=334
        dacList[5]=374
        dacList[6]=362
        dacList[7]=344
        dacList[8]=356      
        dacList[10]=340
        dacList[11]=374
        dacList[12]=360
        dacList[13]=382
        dacList[14]=418        
    elif board==8:
        qMin=1
        cdList=[4];chList=[4,9,14];
        chList=[4,9];cdList=[4];#TDR
        #cdList=[4];
        #chList=[14]
        #cdList=range(0,8);chList=[4]#,9,14];
        #cdList=[0];dacList=range(290,390,10);chList=list(range(0,15));qStep=2;
        #chList=list(range(0,25))
        delayList=[2500]
        dacRef=290#Vthcor computed for this value
        dacList={}
        dacList[0]=   345 
        dacList[1]=   335  
        dacList[2]=   290
        dacList[3]=   340
        dacList[4]=   345
        dacList[5]=   340
        dacList[6]=   335#TOAfrac=0.2
        dacList[7]=   305#TOAfrac=0.2
        dacList[8]=   330
        dacList[9]=   295 
        dacList[10]=  365
        dacList[11]=  355
        dacList[12]=  330 
        dacList[13]=  360#large TOAfrac
        dacList[14]=  310
    elif board==13:
        #chList=list(range(0,6))+list(range(7,15))
        #chList=[3]#,12,21]
        #dacList=[380,400]#range(300,440,10)
        #chList=[0]#TDR
        chList=[0,5,10]
        dacRef=305#Vthcor computed for this value
        dacList={}
        dacList[0]=320
        dacList[1]=305
        dacList[2]=330
        dacList[3]=315
        dacList[4]=305
        dacList[5]=385
        dacList[7]=310
        dacList[8]=335      
        dacList[9]=325  
        dacList[10]=320
        dacList[11]=345
        dacList[12]=365
        dacList[13]=345
        dacList[14]=350
        # dacList[15]=300
        # dacList[16]=380
        # dacList[17]=330
        # dacList[18]=390
        # dacList[19]=370      
        # dacList[20]=350
        # dacList[21]=340
        # dacList[22]=430
        # dacList[23]=400
        # dacList[24]=360
    elif board==15:
        chList=[4,9,14,19,24]
        cdList=[0,4]
        dacList=range(300,410,10)
        dacList={}
        dacList[0]=330
        dacList[1]=310
        dacList[2]=340
        dacList[3]=330
        dacList[4]=320
        dacList[5]=400
        dacList[7]=320
        dacList[8]=350      
        dacList[9]=340  
        dacList[10]=330
        dacList[11]=350
        dacList[12]=370
        dacList[13]=360
        dacList[14]=360
        dacList[15]=300
        dacList[16]=380
        dacList[17]=330
        dacList[18]=390
        dacList[19]=370      
        dacList[20]=350
        dacList[21]=340
        dacList[22]=430
        dacList[23]=400
        dacList[24]=360        
    elif board==18:
        dacList={}
        dacList[0]=360
        dacList[1]=390
        dacList[2]=406
        dacList[3]=340
        #dacList[4]=440
        dacList[5]=360
        #dacList[6]=
        #dacList[7]=
        #dacList[8]=      
        dacList[9]=356  
        dacList[10]=344
        dacList[11]=336
        dacList[12]=326
        dacList[13]=376
        dacList[14]=376



    if chList==None:
        chList=dacList.keys()
        #chList=list(range(15,25))+list(range(0,15))

        
    for ch in chList:
        for cd in cdList:
            #dac list
            dac=dacList[ch]        
            #dacListLocal=list(range(dac,dac+41,8))
            #dacListLocal=list(range(dac-20,dac+21,10))
            #dacListLocal=list(range(dac-8,dac+1,2))
            #dacListLocal=list(range(dac-15,dac+1,5))
            dacListLocal=[dac]
            dacListLocal=[dacRef+20,dacRef+50,dacRef+80]

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
                        
                    f.write(cmd+"\n sleep 5 \n")
                    
                ###############################
                # measure TOA
                ###############################
                #for Q in range(3,22,1):
                #for Q in list(range(3,10,1))+list(range(10,27,4)):
                #for Q in [6,8]:#5,26]:#,8,10,14,16,18,20,22]:
                #for Q in [5,6,7,26]:#5,6,7]:#,8]#,26]:#5,26]:#,8,10,14,16,18,20,22]:
                for Q in [20,40]:#ATT TRIG EXT
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
                    f.write(cmd+"\n sleep 5 \n")



                    #python scripts/measureTOA.py --skipExistingFile True -N $N --debug False --display False --checkOFtoa False --checkOFtot False  --board 8 --ch $ch --useExt True --delayMin 1800 --delayMax 2300 --delayStep 10  --out Data/$NAME --DAC $DAC --Cd $cd  >& 'Data/'$NAME'-'$ch'-'$DAC'.log'



print (" ************ CHECK TRIG EXT ***************")
