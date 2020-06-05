#!/usr/bin/env python

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
# Import Modules                                                             # 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
import sys, os, string, shutil,pickle, subprocess, math, getpass, collections,glob

from optparse import OptionParser
from math import *
from time import *

import numpy as np
from matplotlib import pyplot as plt

from Utils import *


###########################################################################
# command line arguments
###########################################################################

print (sys.argv)

parser = OptionParser()
parser.add_option("-f","--fileList", help="file containing a list of input file", default=None)
parser.add_option("-i","--inputDir", help="Data location", default=None)
parser.add_option("-s","--select", help="select only file names containing this string", default="")
parser.add_option("-d","--display", help="display summary plots on screen", default=False,action="store_true")
parser.add_option("--xmax", help="max of x axis", default=None,type=int)
parser.add_option("--xmin", help="min of x axis", default=None,type=int)
parser.add_option("-a","--allPlots", help="make all plots", default=False,action="store_true")
(options, args) = parser.parse_args()

#make list of input files
fileNameList=glob.glob(options.inputDir+"/*"+options.select+"*.txt")


###########################################################################
# get all data and compute efficiency
###########################################################################

thresDict={}
allData=collections.OrderedDict()
for fileName in fileNameList:

    # extract information from the file name
    board,ch,cd,thres,vthc,Q=getInfoFromFileName(fileName)

    #get data
    NArray,thresArray,nHitArray,nHit2Array=readThresFile(fileName)
    
    #compute eff
    effArray=nHitArray/NArray
    effErArray=np.sqrt(effArray*(1-effArray)/NArray)
    eff2Array=nHit2Array/NArray
    eff2ErArray=np.sqrt(eff2Array*(1-eff2Array)/NArray)
    allData[fileName]=(thresArray,effArray,effErArray,eff2Array,eff2ErArray)

    #threshold
    thres,eff,eff2=getThreshold(thresArray,nHitArray,nHit2Array,NArray)
    thresDict[(fileName,board,ch,cd,Q)]=thres

###########################################################################
# make efficiency plots
###########################################################################

#define figure 
figEff=plt.figure('Efficiency')
axEff = figEff.add_subplot(1,1,1)
axEff.set_ylim(top=1.2)#+0.1*len(allData))

counter=0
for fileName in sorted(allData.keys(),key=lambda n: getInfoFromFileName(n)[1]):
    counter+=1

    # extract information from the file name
    board,ch,cd,thres,vthc,Q=getInfoFromFileName(fileName)
    label="B"+str(board)+" ch"+str(ch)+" Qdac="+str(Q)

    #get data
    data=allData[fileName]
    thresArray,effArray,effErArray,eff2Array,eff2ErArray=data

    #common eff plot
    plt.figure(figEff.number)
    plt.plot(thresArray,effArray,label=label,color=colors[counter-1])

    # individual plot
    fig, ax = plt.subplots()
    ax.set_ylim(top=1.3)
    if options.xmax is not None:
        ax.set_xlim(right=options.xmax)
    if options.xmin is not None:
        ax.set_xlim(left=options.xmin)
    plt.plot(thresArray,effArray,label="Eff")
    plt.plot(thresArray,eff2Array,label="Eff without 127")
    plt.legend(loc='upper left')
    if options.allPlots:plt.savefig("Thres_"+os.path.basename(fileName)+".pdf")
    plt.close()

plt.figure('Efficiency')
if options.xmax is not None:
    axEff.set_xlim(right=options.xmax)
if options.xmin is not None:
    axEff.set_xlim(left=options.xmin)
axEff.set_xlabel("Threshold", fontsize = 10)
axEff.set_ylabel("Efficiency", fontsize = 10)
#plt.legend(loc='upper right', prop={"size":6})
plt.legend(bbox_to_anchor=(1.1, 1.0),loc='upper right', prop={"size":6})
plt.savefig("Thres_SummaryEff.pdf")



###########################################################################
# compute Vthc
###########################################################################

thresRef=int(np.mean(list(thresDict.values())))
print ("Reference threshold (DAC10bit): ",thresRef)
for key in sorted(thresDict.keys(),key=lambda n:n[2]):
    fileName,board,ch,cd,Q=key
    thres=thresDict[key]

    vthc=int(64+(thresRef-thres)*0.4/0.8)
    print ("        bit_vth_cor["+str(ch)+"]: "+str(vthc)+"   #"+str(thres))


    if vthc<0 or vthc>126:
        print ("PRB vthc !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        break



#display figures
if options.display:
    plt.show()

