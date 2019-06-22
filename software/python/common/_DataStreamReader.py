#!/usr/bin/env python3
#################################################################
import sys
import os
import rogue
import time
import random
import argparse
import pyrogue as pr
import pyrogue.gui
import numpy as np
import rogue.utilities.fileio
import statistics
import math
import matplotlib.pyplot as plt

class EventValue(object):
  def __init__(self, SeqCnt, TotOverflow, TotData, ToaOverflow, ToaData, Hit):
     self.SeqCnt      = SeqCnt
     self.TotOverflow = TotOverflow
     self.TotData     = TotData
     self.ToaOverflow = ToaOverflow
     self.ToaData     = ToaData
     self.Hit         = Hit

def ParseDataWord(dataWord):
    # Parse the 32-bit word
    SeqCnt      = (dataWord >> 19) & 0x1FFF
    TotOverflow = (dataWord >> 18) & 0x1
    TotData     = (dataWord >>  9) & 0x1FF
    ToaOverflow = (dataWord >>  8) & 0x1
    ToaData     = (dataWord >>  1) & 0x7F
    Hit         = (dataWord >>  0) & 0x1
    return EventValue(SeqCnt, TotOverflow, TotData, ToaOverflow, ToaData, Hit)

#################################################################

class MyEventReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)
        self.lastTOT = 0
        self.printNext = 0
        self.printNextEn = 0
        self.PrintData = 1

    def _acceptFrame(self,frame):
        # Get the payload data
        p = bytearray(frame.getPayload())
        # Return the buffer index
        frame.read(p,0)
        # Check for a modulo of 32-bit word 
        if ((len(p) % 4) == 0):
            count = int(len(p)/4)
            # Combine the byte array into 32-bit word array
            hitWrd = np.frombuffer(p, dtype='uint32', count=count)
            # Loop through each 32-bit word
            for i in range(count):
                # Parse the 32-bit word
                dat = ParseDataWord(hitWrd[i])
                # Print the event if hit
                #if (dat.Hit > 0):
                #if (dat.Hit > 0) or (self.printNext == 1 and self.printNextEn == 1) or (dat.TotData != 0x1fc and dat.TotData != self.lastTOT):
                if (dat.Hit > 0) or (self.printNext == 1 and self.printNextEn == 1):

                    self.lastTOT = dat.TotData

                    if (self.printNext == 1) and (dat.Hit == 0):
                        self.printNext = 0
                    else:
                        self.printNext = 1

                    if not (dat.ToaOverflow == 1 and dat.ToaData != 0x7f) and (self.PrintData == 1) and (i == 1):

                        print( 'Event[SeqCnt=0x%x]: (TotOverflow = %r, TotData = 0x%x), (ToaOverflow = %r, ToaData = 0x%x), hit=%r' % (
                                dat.SeqCnt,
                                dat.TotOverflow,
                                dat.TotData,
                                dat.ToaOverflow,
                                dat.ToaData,
                                dat.Hit,
                        ))
#################################################################
# Class for Reading the Data from File
class MyFileReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)
        self.HitData = []
        self.HitDataTOTf_vpa = []
        self.HitDataTOTf_tz = []
        self.HitDataTOTc_vpa = []
        self.HitDataTOTc_tz = []
        self.HitDataTOTc_int1_vpa = []
        self.HitDataTOTc_int1_tz = []
        self.HitDataTOTf_vpa_temp = 0
        self.HitDataTOTc_vpa_temp = 0
        self.HitDataTOTf_tz_temp = 0
        self.HitDataTOTc_tz_temp = 0
        self.HitDataTOTc_int1_vpa_temp = 0
        self.HitDataTOTc_int1_tz_temp = 0

    def _acceptFrame(self,frame):
        # Get the payload data
        p = bytearray(frame.getPayload())
        # Return the buffer index
        frame.read(p,0)
        # Check for a modulo of 32-bit word 
        if ((len(p) % 4) == 0):
            count = int(len(p)/4)
            # Combine the byte array into 32-bit word array
            hitWrd = np.frombuffer(p, dtype='uint32', count=count)
            # Loop through each 32-bit word
            for i in range(count):
                # Parse the 32-bit word
                dat = ParseDataWord(hitWrd[i])
                # Print the event if hit

                if (dat.Hit > 0) and (dat.ToaOverflow == 0):
                   
                    self.HitData.append(dat.ToaData)
                
                if (dat.Hit > 0) and (dat.TotData != 0x1fc):
    
                    self.HitDataTOTf_vpa_temp = ((dat.TotData >>  0) & 0x3) + dat.TotOverflow*math.pow(2,2)
                    self.HitDataTOTc_vpa_temp = (dat.TotData >>  2) & 0x7F
                    self.HitDataTOTc_int1_vpa_temp = (((dat.TotData >>  2) + 1) >> 1) & 0x3F
                    #if ((dat.TotData >>  2) & 0x1) == 1:
                    self.HitDataTOTf_vpa.append(self.HitDataTOTf_vpa_temp)
                    self.HitDataTOTc_vpa.append(self.HitDataTOTc_vpa_temp)
                    self.HitDataTOTc_int1_vpa.append(self.HitDataTOTc_int1_vpa_temp)

                if (dat.Hit > 0) and (dat.TotData != 0x1f8):

                    self.HitDataTOTf_tz_temp = ((dat.TotData >>  0) & 0x7) + dat.TotOverflow*math.pow(2,3)
                    self.HitDataTOTc_tz_temp = (dat.TotData >>  3) & 0x3F
                    self.HitDataTOTc_int1_tz_temp = (((dat.TotData >>  3) + 1) >> 1) & 0x1F
                    self.HitDataTOTf_tz.append(self.HitDataTOTf_tz_temp)                    
                    self.HitDataTOTc_tz.append(self.HitDataTOTc_tz_temp)
                    self.HitDataTOTc_int1_tz.append(self.HitDataTOTc_int1_tz_temp)
                   
#################################################################

