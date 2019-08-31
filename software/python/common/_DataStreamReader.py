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
import csv
import click

#################################################################

class PixValue(object):
  def __init__(self, PixelIndex, TotOverflow, TotData, ToaOverflow, ToaData, Hit, Sof):
     self.PixelIndex  = PixelIndex
     self.TotOverflow = TotOverflow
     self.TotData     = TotData
     self.ToaOverflow = ToaOverflow
     self.ToaData     = ToaData
     self.Hit         = Hit
     self.Sof         = Sof

class EventValue(object):
  def __init__(self):
     self.FormatVersion     = None
     self.PixReadIteration  = None
     self.ReadoutSize       = None
     self.SeqCnt            = None
     self.TrigCnt           = None
     self.pixValue          = None
     self.dropTrigCnt       = None

def ParseDataWord(dataWord):
    #Parse the 32-bit word
    PixelIndex  = (dataWord >> 24) & 0x1F
    TotOverflow = (dataWord >> 20) & 0x1
    TotData     = (dataWord >> 11) & 0x1FF
    ToaOverflow = (dataWord >> 10) & 0x1
    ToaData     = (dataWord >>  3) & 0x7F
    Hit         = (dataWord >>  2) & 0x1
    Sof         = (dataWord >>  0) & 0x3

    #print( "{:028b}".format(dataWord) )
    return PixValue(PixelIndex, TotOverflow, TotData, ToaOverflow, ToaData, Hit, Sof)

def ParseFrame(frame):
    # Next we can get the size of the frame payload
    size = frame.getPayload()
    
    # To access the data we need to create a byte array to hold the data
    fullData = bytearray(size)
    
    # Next we read the frame data into the byte array, from offset 0
    frame.read(fullData,0)

    # Fill an array of 32-bit formatted word
    wrdData = [None for i in range(3+512*32+1)]
    wrdData = np.frombuffer(fullData, dtype='uint32', count=(size>>2))
    
    # Parse the data and data to data frame
    eventFrame = EventValue()
    eventFrame.FormatVersion     = (wrdData[0] >>  0) & 0xFFF
    eventFrame.PixReadIteration  = (wrdData[0] >> 12) & 0x1FF
    eventFrame.ReadoutSize       = (wrdData[0] >> 27) & 0x1F
    eventFrame.SeqCnt            = wrdData[1]
    eventFrame.TrigCnt           = wrdData[2]
    numPixValues = (eventFrame.ReadoutSize+1)*(eventFrame.PixReadIteration+1)
    eventFrame.pixValue  = [None for i in range(numPixValues)]
    for i in range(numPixValues):
        eventFrame.pixValue[i] = ParseDataWord(wrdData[3+i])
    eventFrame.dropTrigCnt = wrdData[numPixValues+3]

    return eventFrame

#################################################################

# Class for printing out events
class PrintEventReader(rogue.interfaces.stream.Slave):
    # Init method must call the parent class init
    def __init__(self, cvsDump=False):
        super().__init__()
        self.count   = 0
        self.cvsDump = cvsDump
        if cvsDump:
            self.file   = [None for i in range(2)]
            self.writer = [None for i in range(2)]
            for i in range(2):
                self.file[i]   = open(f'fpag{i}.csv', 'w', newline='') 
                self.writer[i] = csv.writer(self.file[i])
                self.writer[i].writerow([
                    'SeqCnt',       # 0 = SeqCnt
                    'TrigCnt',      # 1 = TrigCnt
                    'DropTrigCnt',  # 2 = DropTrigCnt
                    'pixIndex',     # 3 = pixIndex
                    'TotOverflow',  # 4 = TotOverflow
                    'TotData',      # 5 = TotData
                    'ToaOverflow',  # 6 = ToaOverflow
                    'ToaData',      # 7 = ToaData
                    'Hit',          # 8 = Hit
                    'Sof',          # 9 = Sof
                ])
                
    # Method which is called when a frame is received
    def _acceptFrame(self,frame):

        # First it is good practice to hold a lock on the frame data.
        with frame.lock():
            eventFrame = ParseFrame(frame)
                
            # Print out the event
            header_still_needs_to_be_printed = True
            for i in range( len(eventFrame.pixValue) ):
                pixel = eventFrame.pixValue[i]
                pixIndex = pixel.PixelIndex
                
                #if pixel.ToaOverflow != 1: #make sure this pixel is worth printing
                if (pixel.Hit != 0) and (pixel.ToaData != 0x7F): #make sure this pixel is worth printing
                    if header_still_needs_to_be_printed: #print the header only once per pixel
                        print('FPGA {:#}'.format( frame.getChannel() ) +
                              ', payloadSize(Bytes) {:#}'.format( frame.getPayload() ) +
                              ', FormatVersion {:#}'.format(eventFrame.FormatVersion) +
                              ', PixReadIteration {:#}'.format(eventFrame.PixReadIteration) +
                              ', ReadoutSize {:#}'.format(eventFrame.ReadoutSize) + 
                              ', DropTrigCnt 0x{:X}'.format(eventFrame.dropTrigCnt) + 
                              ', SeqCnt {:#}'.format(eventFrame.SeqCnt) )
                        print('    Pixel : TotOverflow | TotData | ToaOverflow | ToaData | Hit | Sof') 
                        header_still_needs_to_be_printed = False

                    print('    {:>#5} | {:>#11} | {:>#7} | {:>#11} | {:>#7} | {:>#3} | {:>#3}'.format(
                        pixIndex,
                        pixel.TotOverflow,
                        pixel.TotData,
                        pixel.ToaOverflow,
                        pixel.ToaData,
                        pixel.Hit,
                        pixel.Sof)
                    )
                    
                # Check if dumping to .CVS file
                if self.cvsDump:
                    self.writer[frame.getChannel()].writerow([
                        eventFrame.SeqCnt,     # 0 = SeqCnt
                        eventFrame.TrigCnt,    # 1 = TrigCnt
                        eventFrame.dropTrigCnt,# 2 = DropTrigCnt
                        pixIndex,           # 3 = pixIndex
                        pixel.TotOverflow,  # 4 = TotOverflow
                        pixel.TotData,      # 5 = TotData
                        pixel.ToaOverflow,  # 6 = ToaOverflow
                        pixel.ToaData,      # 7 = ToaData
                        pixel.Hit,          # 8 = Hit
                        pixel.Sof,          # 9 = Sof
                    ])                
                        
            self.count += 1
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
        # First it is good practice to hold a lock on the frame data.
        with frame.lock():
            eventFrame = ParseFrame(frame)
            for i in range( len(eventFrame.pixValue) ):
                dat = eventFrame.pixValue[i]

                if (dat.Hit > 0) and (dat.ToaOverflow == 0):
                    self.HitData.append(dat.ToaData)
                
                if (dat.Hit > 0) and (dat.TotData != 0x1fc):
                    self.HitDataTOTf_vpa_temp = ((dat.TotData >>  0) & 0x3) + dat.TotOverflow*math.pow(2,2)
                    self.HitDataTOTc_vpa_temp = (dat.TotData >>  2) & 0x7F
                    self.HitDataTOTc_int1_vpa_temp = (((dat.TotData >>  2) + 1) >> 1) & 0x3F
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

# Class for Reading Data output by pixels
class MyPixelReader(rogue.interfaces.stream.Slave):

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
        # First it is good practice to hold a lock on the frame data.
        with frame.lock():
            eventFrame = ParseFrame(frame)

            for i in range( len(eventFrame.pixValue) ):
                dat = eventFrame.pixValue[i]

                if (dat.Hit > 0) and (dat.ToaOverflow == 0):
                    self.HitData.append(dat.ToaData)
                
                if (dat.Hit > 0) and (dat.TotData != 0x1fc):
                    self.HitDataTOTf_vpa_temp = ((dat.TotData >>  0) & 0x3) + dat.TotOverflow*math.pow(2,2)
                    self.HitDataTOTc_vpa_temp = (dat.TotData >>  2) & 0x7F
                    self.HitDataTOTc_int1_vpa_temp = (((dat.TotData >>  2) + 1) >> 1) & 0x3F
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
