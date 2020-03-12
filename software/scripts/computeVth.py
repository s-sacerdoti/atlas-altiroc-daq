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



def getVthc(board,cd,doPrint=False):

    dacMap=getDACList(board)

    dacList=[]
    for key,val in dacMap.items():
        if key[2]!=cd: continue
        dacList.append(val)
    

    
    dacRef=int(np.mean(dacList))

    if doPrint:    print ("        DAC10bit: "+str(dacRef))
    
    vthcMap={}
    for ch in range(15):
        key=(board,ch,cd)
        d=999999999
        if key in dacMap.keys():
            d=dacMap[key]
            vthc=int(64+(dacRef-d)*0.4/0.8)
        else:
            vthc=1

        #print (d,vthc)
        if doPrint:print ("        bit_vth_cor["+str(key[1])+"]: "+str(vthc)+"   #"+str(d)+" "+str(dacRef))
        if vthc<0 or vthc>126:
            print ("PRB vthc !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            break
        vthcMap[ch]=vthc
    return dacRef,vthcMap

if __name__ == "__main__":
  

    parser = argparse.ArgumentParser()
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    parser.add_argument("-b", "--board", type = int, required = False, default = 13,help = "Choose board")
    args = parser.parse_args()

    boardASICAlone=[8,9,10,11,12,14,15]
    cd=0
    if args.board in boardASICAlone:
        cd=4

    getVthc(args.board,cd,True)


