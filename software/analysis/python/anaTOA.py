#!/usr/bin/env python

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
# Import Modules                                                             # 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
import sys, os, string, shutil,pickle, subprocess, math, getpass, collections,glob

from optparse import OptionParser
from math import *
from time import *

import numpy as np
import matplotlib
import matplotlib.gridspec as gridspec
from matplotlib import pyplot as plt
#from scipy import optimize
from Utils import *


###########################################################################
# command line arguments
###########################################################################



parser = OptionParser()
#parser.add_option("-f","--fileName", help="", default=None)
parser.add_option("-N","--Nevents", help="Data location", default=100,type=int)
parser.add_option("-i","--inputDir", help="Data location", default="Data/B8_toa_clkTree/")
parser.add_option("-e","--extra", help="select only file names containing this string", default="")
parser.add_option("--Qmax", help="max Q", default=None,type=int)
parser.add_option("--Qmin", help="min Q", default=None,type=int)
parser.add_option("-a","--allPlots", help="make all plots", default=False,action="store_true")
parser.add_option("-b","--bidim", help="make bidim ", default=False,action="store_true")
(options, args) = parser.parse_args()

fileNameList=glob.glob(options.inputDir+"/*"+options.extra+"*.txt")


DelayStep=9.5582
Qconv=10./13.
delayRef=2450*DelayStep


###########################################################################
# 
###########################################################################

figTOAMean=plt.figure('TOAMean')
axTOAMean = figTOAMean.add_subplot(1,1,1)

figJitter=plt.figure('Jitter')
axJitter = figJitter.add_subplot(1,1,1)

allData=collections.OrderedDict()
LSBList=[]
chList=[]
TOARefList=[]

for fileNb,fileName in enumerate(sorted(fileNameList,key=lambda n: getInfoFromFileName(n)[1])):
    #print (fileName)
    # extra information from the file name
    board,ch,cd,thres,vthc,Q=getInfoFromFileName(fileName)
    label="B"+str(board)+" ch"+str(ch)+" Vth="+str(thres)+" Vthc="+str(vthc)+" Q="+str(Q)

    #get data
    delayMap,dataMap=readTOAFile(fileName,Qconv=Qconv,DelayStep=DelayStep)


    delayList=[]
    delayDACList=[]
    toaMeanList=[]
    jitterList=[]
    allTOAList=[]
    effList=[]
    allDelayList=[]

    counter=0
    nMax=0
    for delay in sorted(dataMap.keys()):
        toaList=np.array(dataMap[delay])

        #extract information
        okTOA=toaList!=127 #used to remove saturated toa
        toaOKList=toaList[okTOA]
        TOAMean=0
        jitter=0

        if len(toaList)>    nMax:
            nMax=len(toaList)
        if len(toaOKList)>10:#compute mean and jitter with at N events
            TOAMean=np.mean(toaOKList)
            jitter=np.std(toaOKList)


        #store information in list
        toaMeanList.append(TOAMean)
        jitterList.append(jitter)
        delayList.append(delay)
        delayDACList.append(delayMap[delay])
        effList.append(len(toaOKList))
        for toa in toaList:
            allTOAList.append(toa)
            allDelayList.append(delay)

    if len(effList)==0: continue
    #convert to np array
    effArray=np.array(effList)/nMax
    delayArray=np.array(delayList)
    toaMeanArray=np.array(toaMeanList)
    jitterArray=np.array(jitterList)
    allDelayArray=np.array(allDelayList)
    allTOAArray=np.array(allTOAList)

    # eff selection
    okEff=effArray>0.5
    print (okEff,all(okEff))
    try:
        delayMin=int(min(delayArray[okEff])*0.99)
        delayMax=int(max(delayArray[okEff])*1.01)
    except:
        delayMin=20000
        delayMax=25000
        
    #compute LSB from a fit
    #params, covariance = optimize.curve_fit(pol1, delayArray[okEff],toaMeanArray[okEff],p0=[1/20, 10000])
    params=np.polyfit(delayArray[okEff],toaMeanArray[okEff], 1)

    LSBTOA=0
    if params[0]!=0:
        LSBTOA=abs(1/params[0])
    TOARef=pol1(delayRef , params[0], params[1])*LSBTOA
    
    print (board,ch,cd,thres,vthc,Q,TOARef,LSBTOA)

    #TOA vs delay 2D Hist
    if options.bidim:
        xedges = range(delayMin,delayMax,10)
        yedges = range(0,128,1)
        HTOA, xedges, yedges = np.histogram2d(allDelayArray, allTOAArray, bins=(xedges, yedges))
        HTOA = HTOA.T  # Let each row list bins with common y range.
        HTOA[HTOA==0]=np.nan
        current_cmap = matplotlib.cm.get_cmap()
        current_cmap.set_bad(color='white')
        X, Y = np.meshgrid(xedges, yedges)        


    # all plots with LSB applied
    fig, ax = plt.subplots(3,1)
    ax[0].plot(delayArray,effArray,label="eff")
    ax[0].set_ylabel("Efficiency", fontsize = 10)
    ax[1].plot(delayArray,toaMeanArray*LSBTOA,label="TOA")
    ax[1].set_ylabel("<TOA> [ps]", fontsize = 10)
    ax[2].plot(delayArray,jitterArray*LSBTOA,label="Jitter")
    ax[2].set_ylabel("jitter [ps]", fontsize = 10)
    ax[2].set_xlabel("Delay [ps]", fontsize = 10)
    if options.allPlots:plt.savefig("TOA_"+os.path.basename(fileName)+"_All.pdf")
    plt.close()

    # TOA mean only without LSB applied
    figTOA=plt.figure()
    gs = gridspec.GridSpec(3,1)
    ax1 = plt.subplot(gs[:2, :])
    ax1.scatter(delayArray[okEff],toaMeanArray[okEff],label="TOA with eff cut", facecolors='none', edgecolors='green')
    ax1.plot(delayArray[okEff], pol1(delayArray[okEff], params[0], params[1]),label='pol1',color='r')
    if options.bidim:    ax1.pcolormesh(X, Y, HTOA,cmap=plt.cm.jet)
    ax1.set_ylabel("<TOA> [dac]", fontsize = 10)
    ax1.set_xlabel("Delay [ps]", fontsize = 10)
    ax1.set_xlim(left=delayMin)
    ax1.set_xlim(right=delayMax)
    ax1.text(0.8,0.8,'LSB='+str(round(LSBTOA,1))+"ps",horizontalalignment='center',verticalalignment='center', transform = ax1.transAxes)
    ax2 = plt.subplot(gs[2, :]) 
    ax2.scatter(delayArray[okEff],toaMeanArray[okEff]-pol1(delayArray[okEff], params[0], params[1]),label="TOA with eff cut", facecolors='none', edgecolors='green')
    ax2.set_xlim(left=delayMin)
    ax2.set_xlim(right=delayMax)
    ax2.set_ylabel("Fit residual", fontsize = 10)
    ax2.set_xlabel("Delay [ps]", fontsize = 10)
    if options.allPlots:plt.savefig("TOA_"+os.path.basename(fileName)+"_toaMean.pdf")
    plt.close()

    #comparison plots TOAMean
    plt.figure(figTOAMean.number)
    axTOAMean.scatter(delayArray[okEff],toaMeanArray[okEff]*LSBTOA,s=10,label=label, color=colors[fileNb])#, markersize=5)

    #comparison plots Jitter
    plt.figure(figJitter.number)
    axJitter.scatter(delayArray[okEff],jitterArray[okEff]*LSBTOA,s=10,label=label, color=colors[fileNb])#, markersize=5)

    #save some data
    LSBList.append(LSBTOA)
    chList.append(ch)
    TOARefList.append(TOARef)


#toaMean summary plot
plt.figure(figTOAMean.number)
#axToaMean.set_ylim(top=1.2)
axTOAMean.set_xlabel("Delay [ps]", fontsize = 10)
axTOAMean.set_ylabel("<TOA> [ps]", fontsize = 10)
plt.legend(loc='upper right', prop={"size":6})
plt.savefig("TOA_SummaryTOAMean.pdf")


#jitter summary plot
plt.figure(figJitter.number)
#axToaMean.set_ylim(top=1.2)
axJitter.set_xlabel("Delay [ps]", fontsize = 10)
axJitter.set_ylabel("<TOA> [ps]", fontsize = 10)
plt.legend(loc='upper right', prop={"size":6})
plt.savefig("TOA_SummaryJitter.pdf")

#convert
chArray=np.array(chList)
LSBArray=np.array(LSBList)
TOARefArray=np.array(TOARefList)


figLSB=plt.figure('LSB')
axLSB = figLSB.add_subplot(1,1,1)
axLSB.scatter(chArray,LSBArray)
axLSB.set_xlabel("Channel nb", fontsize = 10)
axLSB.set_ylabel("LSB", fontsize = 10)
plt.savefig("TOA_LSBvsCh.pdf")

figTOARef=plt.figure('TOARef')
axTOARef = figTOARef.add_subplot(1,1,1)
axTOARef.scatter(chArray,TOARefArray)
axTOARef.set_xlabel("Channel number", fontsize = 10)
axTOARef.set_ylabel("TOA for delay="+str(int(delayRef))+"ps [ps]", fontsize = 10)
plt.savefig("TOA_TOARefvsCh.pdf")



