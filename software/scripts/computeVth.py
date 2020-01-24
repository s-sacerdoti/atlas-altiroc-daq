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
dacList[13]=  360
dacList[14]=  310



dacRef=290

i=0
for i,d in dacList.items():

    vthc=int(64+(dacRef-d)*0.4/0.8)


    
    print ("bit_vth_cor["+str(i)+"]:"+str(vthc))
