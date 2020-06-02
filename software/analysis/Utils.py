#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
# Import Modules                                                             # 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
import sys, os, string, shutil,pickle, subprocess, math
import getpass
from array import array
from math import *
from time import *
import time
import numpy as np

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
# Functions                                                                  # 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#


# get info from file name
def getInfoFromFileName(filename):
    board=999
    ch=999
    cd=999
    thres=999
    Q=-1
    vecfilename=filename.split("_")
    if "B" in vecfilename:board=int(vecfilename[vecfilename.index("B")+1])
    if "ch" in vecfilename:ch=int(vecfilename[vecfilename.index("ch")+1])
    if "cd" in vecfilename:cd=int(vecfilename[vecfilename.index("cd")+1])
    if "thres" in vecfilename:thres=int(vecfilename[vecfilename.index("thres")+1])
    if "Q" in vecfilename:Q=int(vecfilename[vecfilename.index("Q")+1])

    return board,ch,cd,thres,Q
    
# read threshold scan file
def readThresFile(filename):
    thresArray=[]
    NArray=[]
    nHitArray=[]
    nHit2Array=[]#Saturated TOA removed from this counter
    f=open(filename)
    for line in [line.strip() for line in f.readlines()]:
        if line.find("dacList")>=0: continue
        #the input file should contains: thres, number of events, nb of hits, nb of hits not saturated (!=127)
        thres,N,nHit,nHit2=line.split()
        thresArray.append(float(thres))
        nHitArray.append(float(nHit))
        NArray.append(float(N))
        nHit2Array.append(float(nHit2))
    f.close()
    thresArray=np.array(thresArray)
    nHitArray=np.array(nHitArray)
    nHit2Array=np.array(nHit2Array)
    return NArray,thresArray,nHitArray,nHit2Array



def getThreshold(thresArray,nHitArray,nHit2Array,NArray):
    myThres = 999
    myIndex = 999
    eff2=0
    eff=0
    for thres_index, thres  in enumerate(thresArray):
        N=NArray[thres_index]
        if thres_index>1 and nHitArray[thres_index]/N>0.95 and nHit2Array[thres_index]>0:
            myThres = thresArray[thres_index]
            myIndex=thres_index
            eff2=nHit2Array[thres_index]/float(N)
            eff=nHitArray[thres_index]/float(N)

            
    # print ("**************************************")
    # print (eff2)
    # thresFlag="ok"
    # if eff2==0:
    #     print ("Can't find a threshold")
    # elif eff2>0.8:
    #     print('Threshold = %d '% (myThres))
    # else:
    #     print('Threshold = %d but LARGE FRAC OF TOA 127 (%f)'% (myThres,1-eff2))
    #     thresFlag="PRB!!!!!!!!!"
    # print ("**************************************")
    return myThres,eff,eff2
