#!/usr/bin/env python3
import pyrogue as pr

import rogue.interfaces.stream

import numpy as np

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

class ExampleEventReader(rogue.interfaces.stream.Slave):

    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)

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
                # Print the event
                print( 'Event[SeqCnt=0x%x]: (TotOverflow = %r, TotData = 0x%x), (ToaOverflow = %r, ToaData = 0x%x), hit=%r' % (
                        dat.SeqCnt,
                        dat.TotOverflow,
                        dat.TotData,
                        dat.ToaOverflow,
                        dat.ToaData,
                        dat.Hit,
                ))
        else:
            print ('Event dumped')    
        
