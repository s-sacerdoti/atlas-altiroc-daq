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
    
    parser.add_argument("--infile", nargs ='+', required = True, help = "input files")
    parser.add_argument("--asics", nargs ='+', required = True, help = "Which ASIC Board(s) was used in this test")
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

        number_of_fpgas = len(args.asics)

        #name output equal to input
        output_files = []
        for fpga_index in range(number_of_fpgas):
            inFile_base = inFile[:inFile.find('.dat')]
            outFile_base = inFile_base+'_asicB'+str(args.asics[fpga_index])
            if args.suffix != None: outFile_base += '_'+args.suffix
            outFile += '.txt'
            output_files.append(outFile)

        # Create the File reader streaming interface
        dataReader = rogue.utilities.fileio.StreamReader()

        # Create the Event reader streaming interface
        dataStream = feb.FrameToTextConverter(output_files)

        # Connect the file reader ---> event reader
        pr.streamConnect(dataReader, dataStream)

        # Open the file
        dataReader.open(inFile)

        # Close file once everything processed
        dataReader.closeWait()

        #auxChList.append(pixelID[0])

        for fpga_index in range(number_of_fpgas):
            myfile = open(output_files[fpga_index],'a')
            myfile.write(output_text_data[fpga_index])
            myfile.close()

        for i in range(len(output_files)):
            if os.path.exists(output_files[i]):
                print(' File created:'+output_files[i])
#################################################################
if __name__ == "__main__":
    args = parse_arguments()
    print(args)    
    convertTBdata(args.infile)
