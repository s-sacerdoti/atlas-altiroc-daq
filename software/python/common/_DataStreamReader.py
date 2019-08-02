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
     self.StartPix          = None
     self.StopPix           = None
     self.SeqCnt            = None
     self.pixValue          = None
     self.footer            = None


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
    wrdData = [None for i in range(2+512*32+1)]
    wrdData = np.frombuffer(fullData, dtype='uint32', count=(size>>2))
    
    # Parse the data and data to data frame
    eventFrame = EventValue()
    eventFrame.FormatVersion     = (wrdData[0] >>  0) & 0xFFF
    eventFrame.PixReadIteration  = (wrdData[0] >> 12) & 0x1FF
    eventFrame.StartPix          = (wrdData[0] >> 22) & 0x1F
    eventFrame.StopPix           = (wrdData[0] >> 27) & 0x1F
    eventFrame.SeqCnt            = wrdData[1]
    numPixValues = (eventFrame.StopPix-eventFrame.StartPix+1)*(eventFrame.PixReadIteration+1)
    eventFrame.pixValue  = [None for i in range(numPixValues)]
    for i in range(numPixValues):
        eventFrame.pixValue[i] = ParseDataWord(wrdData[2+i])
    eventFrame.footer = wrdData[numPixValues+2]

    return eventFrame

#################################################################

class MyEventReader(rogue.interfaces.stream.Slave):
    # Init method must call the parent class init
    def __init__(self):
        super().__init__()
        self.count = 0

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
                #if (pixel.Hit != 0) and (pixel.ToaData != 0x7F) : #make sure this pixel is worth printing
                if (pixel.Hit != 0) and ((pixel.ToaData != 0x7F) or (pixel.TotData !=0)): #make sure this pixel is worth printing
                    if header_still_needs_to_be_printed: #print the header only once per pixel
                        print('payloadSize(Bytes) {:#}'.format( frame.getPayload() ) +
                              ', FormatVersion {:#}'.format(eventFrame.FormatVersion) +
                              ', PixReadIteration {:#}'.format(eventFrame.PixReadIteration) +
                              ', StartPix {:#}'.format(eventFrame.StartPix) +
                              ', StopPix {:#}'.format(eventFrame.StopPix) + 
                              ', footer 0x{:X}'.format(eventFrame.footer) + 
                              ', SeqCnt {:#}'.format(eventFrame.SeqCnt) )
                        print('    Pixel : TotOverflow | TotData | ToaOverflow | ToaData | Hit | Sof | TotData_c | TotData_f') 
                        header_still_needs_to_be_printed = False

                    print(' {:>#5} | {:>#11} | {:>#7} | {:>#11} | {:>#7} | {:>#3} | {:>#3}| {:>#9}| {:>#9}'.format(
                        pixIndex,
                        pixel.TotOverflow,
                        pixel.TotData,
                        pixel.ToaOverflow,
                        pixel.ToaData,
                        pixel.Hit,
                        pixel.Sof,
                        (pixel.TotData >>  2) & 0x7F,
                        (pixel.TotData & 0x3)) 
                    )
                
            self.count += 1
#################################################################

# Class for Reading the Data from File
class MyFileReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)
        self.HitData = []
        self.HitDataTOT = []
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
                    #self.HitDataTOTf_vpa_temp = ((dat.TotData >>  0) & 0x3) + dat.TotOverflow*math.pow(2,2)
                    self.HitDataTOT.append(dat.TotData)
                    self.HitDataTOTf_vpa_temp = ((dat.TotData >>  0) & 0x3)
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
#################################################################
#################################################################
##                  Legacy Classes from v1.0.0                 ##
#################################################################
#################################################################
#################################################################

class LegacyEventValue(object):
  def __init__(self, SeqCnt, TotOverflow, TotData, ToaOverflow, ToaData, Hit):
     self.SeqCnt      = SeqCnt
     self.TotOverflow = TotOverflow
     self.TotData     = TotData
     self.ToaOverflow = ToaOverflow
     self.ToaData     = ToaData
     self.Hit         = Hit

def LegacyParseDataWord(dataWord):
    # Parse the 32-bit word
    SeqCnt      = (dataWord >> 19) & 0x1FFF
    TotOverflow = (dataWord >> 18) & 0x1
    TotData     = (dataWord >>  9) & 0x1FF
    ToaOverflow = (dataWord >>  8) & 0x1
    ToaData     = (dataWord >>  1) & 0x7F
    Hit         = (dataWord >>  0) & 0x1
    return LegacyEventValue(SeqCnt, TotOverflow, TotData, ToaOverflow, ToaData, Hit)

#################################################################

class LegacyMyEventReader(rogue.interfaces.stream.Slave):

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
                dat = LegacyParseDataWord(hitWrd[i])
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
class LegacyMyFileReader(rogue.interfaces.stream.Slave):

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
                dat = LegacyParseDataWord(hitWrd[i])
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
