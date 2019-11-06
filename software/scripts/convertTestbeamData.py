#!/usr/bin/env python3
#convert testbeam data into txt
#################################################################
                                                               ##
import sys                                                     ##
import rogue                                                   ##
import time                                                    ##
import random                                                  ##
import argparse                                                ##
                                                               ##
import pyrogue as pr                                           ##
import pyrogue.gui                                             ##
import numpy as np                                             ##
import common as feb                                           ##
                                                               ##
import os                                                      ##
import rogue.utilities.fileio                                  ##
#################################################################
def parse_arguments():
    parser = argparse.ArgumentParser()

    # Convert str to bool
    argBool = lambda s: s.lower() in ['true', 't', 'yes', '1']
    
    parser.add_argument("--infile", nargs ='+',required = True, help = "input files")
    parser.add_argument("--boards", nargs ='+', required = True, help = "Which ASIC Board(s) was used in this test")
    parser.add_argument("--suffix",default=None, required = False, help = "additional suffix to be added to file name")

    # Get the arguments
    args = parser.parse_args()
    return args
#################################################################

def convertTBdata(inFiles):
    outFiles = []
    auxChList = []
    for inFile in inFiles:
        print("Opening file "+inFile)
        number_of_fpgas = len(args.boards)

        #name output equal to input
        output_files = []
        for fpga_index in range(number_of_fpgas):
            inFile_base = inFile[:inFile.find('.dat')]
            outFile_base = inFile_base+'_asicB'+str(args.boards[fpga_index])
            if args.suffix != None: outFile_base += '_'+args.suffix
            outFile_base += '.txt'
            output_files.append(outFile_base)


        # Create the File reader streaming interface
        dataReader = rogue.utilities.fileio.StreamReader()

        # Create the Event reader streaming interface
        dataStream = feb.BeamTestFileReader()

        # Connect the file reader ---> event reader
        pr.streamConnect(dataReader, dataStream)

        # Open the file
        dataReader.open(inFile)

        # Close file once everything processed
        dataReader.closeWait()

        HitDataTOA = dataStream.HitDataTOA
        HitDataTOTc = dataStream.HitDataTOTc_vpa
        HitDataTOTf = dataStream.HitDataTOTf_vpa
        overflowTOA = dataStream.TOAOvflow
        overflowTOT = dataStream.TOAOvflow
        pixelID = dataStream.pixelId  
        fpga_channel = dataStream.FPGA_channel
        seq_cnt_list = dataStream.SeqCnt
        trig_cnt_list = dataStream.TrigCnt
        drop_cnt_list = dataStream.DropCnt
        time_stamp_list = dataStream.TimeStamp

        #auxChList.append(pixelID[0])

        cntTOA = len(HitDataTOA)
        cntTOT = len(HitDataTOTc)

        number_of_fpgas = 2

        frames_since_last_write = 0
        output_text_data = ['']*number_of_fpgas
        for frame_index in range( len(HitDataTOA) ):
            if frame_index%100 == 0: 
                print(" reading out frame "+str(frame_index))
            fpga_index = fpga_channel[frame_index]
            seqcnt = seq_cnt_list[frame_index]
            trigcnt = trig_cnt_list[frame_index]
            dropcnt = drop_cnt_list[frame_index]
            time_stamp = time_stamp_list[frame_index]
            
            output_text_data[fpga_index] += 'frame {} {} {} {} {}\n'.format(frame_index,seqcnt,trigcnt,dropcnt,time_stamp)
            for channel in range( len(HitDataTOA[frame_index]) ):
                toa = HitDataTOA[frame_index][channel]
                totc = HitDataTOTc[frame_index][channel]
                totf = HitDataTOTf[frame_index][channel]
                toaOV = overflowTOA[frame_index][channel]
                totOV = overflowTOT[frame_index][channel]
                pixID = pixelID[frame_index][channel]
                output_text_data[fpga_index] += '{} {} {} {} {} {}\n'.format(pixID,toa,totc,totf,toaOV,totOV)

            if frames_since_last_write > 20000:
                for fpga_index in range(number_of_fpgas):
                    if len(output_text_data[fpga_index])==0: continue
                    myfile = open(output_files[fpga_index],'a')
                    myfile.write(output_text_data[fpga_index])
                    myfile.close()
                    output_text_data[fpga_index] = ''
                frames_since_last_write = 0
                #print('{} {} {} {} {} {}\n'.format(pixID,toa,totc,totf,toaOV,totOV))
            else: frames_since_last_write += 1

        for fpga_index in range(number_of_fpgas):
            if len(output_text_data[fpga_index])==0: continue
            myfile = open(output_files[fpga_index],'a')
            myfile.write(output_text_data[fpga_index])
            myfile.close()

        for i in range(len(output_files)):
            if os.path.exists(output_files[i]):
                print(' File created:'+output_files[i])
                print(' channel list = ' ) 
                #print(auxChList[i]) 
#################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)    
    convertTBdata(args.infile)
