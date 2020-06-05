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



parser = OptionParser()
#parser.add_option("-f","--fileName", help="", default=None)
parser.add_option("-f","--fileList", help="file containing a list of input file", default=None)
parser.add_option("-i","--inputDir", help="Data location", default=None)#"Data/B8_toa_clkTree/")
parser.add_option("-s","--select", help="select only file names containing this string", default="")
parser.add_option("-a","--allPlots", help="make all plots for debugging purpose", default=False,action="store_true")
parser.add_option("-d","--display", help="display summary plots on screen", default=False,action="store_true")
parser.add_option("-N","--Nevents", help="Nb of events during data taking. Needed to compute efficiency", default=100,type=int)
parser.add_option("--Qmax", help="max Q", default=None,type=int)
parser.add_option("--Qmin", help="min Q", default=None,type=int)

(options, args) = parser.parse_args()


#make list of input files
fileNameList=getFileList(options.inputDir,options.fileList,options.select,extension="data")

###########################################################################
# some parameters
###########################################################################

LSBTOA=20
LSBTOTC=160
Qconv=10./13.



###########################################################################
# 
###########################################################################

#define figures
figEff=plt.figure('Efficiency')
axEff = figEff.add_subplot(1,1,1)
figTOAmean=plt.figure('TOAmean')
axTOAmean = figTOAmean.add_subplot(1,1,1)
figTOArms=plt.figure('TOArms')
axTOArms = figTOArms.add_subplot(1,1,1)
figTOTCmean=plt.figure('TOTCmean')
axTOTCmean = figTOTCmean.add_subplot(1,1,1)
#figTOTCrms=plt.figure('TOTCrms')
#axTOTCrms = figTOTCrms.add_subplot(1,1,1)

#define dict to store data
allData=collections.OrderedDict()

#loop over files
for fileNb,fileName in enumerate(sorted(fileNameList,key=lambda n: getInfoFromFileName(n)[1])):
    print ("Process: ",fileName)

    # extra informatiaon from the file name
    board,ch,cd,thres,vthc,Q=getInfoFromFileName(fileName)
    label="B"+str(board)+" ch"+str(ch)+" Vth="+str(thres)+" Vthc="+str(vthc)

    #get data
    QArray,QDACArray,pixel_data=readTimeWalkFile(fileName,Qconv=Qconv)

    #initialize list
    effArray = np.zeros(len(QArray))
    TOAmeanArray = np.zeros(len(QArray))-9999.
    TOArmsArray = np.zeros(len(QArray))-9999.
    TOTCmeanArray = np.zeros(len(QArray))-9999.
    TOTCrmsArray = np.zeros(len(QArray))-9999.

    # loop over charges
    for counter,Q in enumerate(QArray):
       QDAC=QDACArray[counter]
        
       #skip when almost no data
       if len(pixel_data[('HitDataTOA',Q)])<=2:
           continue
       
       #compute eff
       toaof=0
       for ele in  pixel_data[('HitDataTOA',Q)]:
           if ele==127:toaof+=1
       eff= float(len(pixel_data[('HitDataTOA',Q)])-toaof)/options.Nevents
       
       #stop here if very low eff (can't compute jitter with very low stat)
       if eff<0.05: continue

       #compute TOA mean and rms without saturated TOA
       okTOA=pixel_data[('HitDataTOA',Q)]!=127 #used to remove saturated toa
       toaVec=pixel_data[('HitDataTOA',Q)][okTOA]
       TOAmean=0
       TOArms=0
       if len(toaVec)>0:
           TOAmean=np.mean(toaVec)*LSBTOA
           TOArms=np.std(toaVec)*LSBTOA

       #compute TOTC mean and rms without saturated TOTC
       okTOTC=pixel_data[('HitDataTOTc',Q)]!=127 #used to remove saturated totc
       totcVec=pixel_data[('HitDataTOTc',Q)][okTOTC]
       TOTCmean=0
       TOTCrms=0
       if len(totcVec)>0:
           TOTCmean=np.mean(totcVec)*LSBTOTC
           TOTCrms=np.std(totcVec)*LSBTOTC

       #fill list
       effArray[counter]=eff
       if not math.isnan(TOAmean):TOAmeanArray[counter]=TOAmean
       if not math.isnan(TOArms):TOArmsArray[counter]=TOArms
       if not math.isnan(TOTCmean):TOTCmeanArray[counter]=TOTCmean
       if not math.isnan(TOTCrms):TOTCrmsArray[counter]=TOTCrms


    # eff plot
    plt.figure(figEff.number)
    plt.plot(QArray,effArray,label=label,color=colors[fileNb])

    # TOA mean
    plt.figure(figTOAmean.number)
    plt.plot(QArray,TOAmeanArray,label=label,color=colors[fileNb])

    # TOA rms
    plt.figure(figTOArms.number)
    plt.plot(QArray,TOArmsArray,label=label,color=colors[fileNb])

    # TOTC mean
    plt.figure(figTOTCmean.number)
    plt.plot(QArray,TOTCmeanArray,label=label,color=colors[fileNb])

    # TOTC rms
    #plt.figure(figTOTCrms.number)
    #plt.plot(QArray,TOTCrmsArray,label=label,color=colors[fileNb])
    


#eff
plt.figure(figEff.number)
if options.Qmax is not None:
    axEff.set_xlim(right=options.Qmax)
if options.Qmin is not None:
    axEff.set_xlim(left=options.Qmin)
axEff.set_ylim(top=1.2)
axEff.set_xlabel("Q [fC]", fontsize = 10)
axEff.set_ylabel("Efficiency", fontsize = 10)
plt.legend(loc='upper right', prop={"size":6})
plt.savefig("TW_SummaryEff.pdf")




#TOA mean
axTOAmean.set_title('Plot done with LSBTOA='+str(LSBTOA)+"ps", fontsize = 11)
plt.figure(figTOAmean.number)
if options.Qmax is not None:
    axTOAmean.set_xlim(right=options.Qmax)
if options.Qmin is not None:
    axTOAmean.set_xlim(left=options.Qmin)
axTOAmean.set_ylim(bottom=0)
axTOAmean.set_ylim(top=127*LSBTOA)
axTOAmean.set_xlabel("Q [fC]", fontsize = 10)
axTOAmean.set_ylabel("<TOA>  [ps]", fontsize = 10)
plt.legend(loc='upper left', prop={"size":6})
plt.savefig("TW_SummaryTOAmean.pdf")


#TOA rms
axTOArms.set_title('Plot done with LSBTOA='+str(LSBTOA)+"ps", fontsize = 11)
plt.figure(figTOArms.number)
if options.Qmax is not None:
    axTOArms.set_xlim(right=options.Qmax)
if options.Qmin is not None:
    axTOArms.set_xlim(left=options.Qmin)
axTOArms.set_ylim(bottom=0)
axTOArms.set_ylim(top=5*LSBTOA)
axTOArms.set_xlabel("Q [fC]", fontsize = 10)
axTOArms.set_ylabel("Jitter  [ps]", fontsize = 10)
plt.legend(loc='upper right', prop={"size":6})
plt.savefig("TW_SummaryTOArms.pdf")




#TOTC mean
axTOTCmean.set_title('Plot done with LSBTOTC='+str(LSBTOTC)+"ps", fontsize = 11)
plt.figure(figTOTCmean.number)
if options.Qmax is not None:
    axTOTCmean.set_xlim(right=options.Qmax)
if options.Qmin is not None:
    axTOTCmean.set_xlim(left=options.Qmin)
axTOTCmean.set_ylim(bottom=0)
axTOTCmean.set_ylim(top=127*LSBTOTC)
axTOTCmean.set_xlabel("Q [fC]", fontsize = 10)
axTOTCmean.set_ylabel("<TOTC> [ps]", fontsize = 10)
plt.legend(loc='upper left', prop={"size":6})
plt.savefig("TW_SummaryTOTCmean.pdf")



# #TOTC rms
# axTOTCrms.set_title('Plot done with LSBTOTC='+str(LSBTOTC)+"ps", fontsize = 11)
# plt.figure(figTOTCrms.number)
# if options.Qmax is not None:
#     axTOTCrms.set_xlim(right=options.Qmax)
# if options.Qmin is not None:
#     axTOTCrms.set_xlim(left=options.Qmin)
# axTOTCrms.set_ylim(bottom=0)
# axTOTCrms.set_ylim(top=127*LSBTOTC)
# axTOTCrms.set_xlabel("Q [fC]", fontsize = 10)
# axTOTCrms.set_ylabel("TOTC rms [ps]", fontsize = 10)
# plt.legend(loc='upper left', prop={"size":6})
# plt.savefig("TW_SummaryTOTCrms.pdf")




#display figures
if options.display:
    plt.show()
