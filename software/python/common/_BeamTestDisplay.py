import datetime
import rogue
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
matplotlib.use('QT5Agg')
import os
import common as feb

#for testing
import time
import random


class beamTestEventDisplay(rogue.interfaces.stream.Slave):
    '''
    Python 3 compatible
    Requires numpy, matplotlib, datetime, os, shutil packages
    
    onlineEventDisplay is a class deisgned to monitor the online outputs from the HGTD ASIC 
    The class monitors per pixel data from 2 channels; TOA, and TOT
    Note that this data must be discrete (bits)
    
    Inputs to the class objects are the per pixel values for TOA and TOT,
    As well as the indices of all the pixels that registered a hit (not overflow) for TOA.
    
    The output is a live matplotlib window that will keep refreshing in the background 
    for every update call to the object, building an integrated image. This image can be reset,
    and snapshots at any given instant can also be taken. Additionally, snapshots of instantaneous data,
    ie from a single triggered event, can also be recorded. These are saved as pdfs.
    
    Note: Font and Figure size should be chosen such that the plot refresh speed is acceptable for monitoring
    A few useful sizes and combinations:
        1. Large :  Font Size = 8, Figure Size = (30,15)
        2. Medium:  Font Size = 6, Figure Size = (15,8)
        3. Small :  Font Size = 4, Figure Size = (10,6)
    
    To initialize:
    myObject = onlineEventDisplay(TOA_range_of_bit_values like (0,127), TOA_range_of_number_of_pixels like (0,24), 
                                  TOA_number_of_bit_values like 128, TOA_number_of_pixels like 5,
                                  TOT_range_of_bit_values like (0,127), TOT_range_of_number_of_pixels like (0,24), 
                                  TOT_number_of_bit_values like 128, TOT_number_of_pixels like 5,
                                  Number_of_pixels_horizontally like 5, Number_of_pixels_vertically like 5,
                                  font_size_to_use_in_plot like 8, figure_size_to_use_in_plot like (30,15),
                                  directory_for_saved_pdf_files like 'path/',
                                  permit_overwriting_of_submit_directory like False)
                                  
    To reset the stored arrays that integrate the number of hits and TOT/TOA values recorded:
    myObject.reset()
    
    '''
    def __init__(self, plot_title='Beam Test Display', toa_xrange=(0,128), toa_xbins=128, tot_xrange=(0,128), tot_xbins=128,
                 xpixels=5, ypixels=5, font_size=6, fig_size=(15,8)):
        '''
        To initialize:
        myObject = onlineEventDisplay(TOA_range_of_bit_values like (0,127), TOA_range_of_number_of_pixels like (0,24), 
                                      TOA_number_of_bit_values like 128, TOA_number_of_pixels like 5,
                                      TOT_range_of_bit_values like (0,127), TOT_range_of_number_of_pixels like (0,24), 
                                      TOT_number_of_bit_values like 128, TOT_number_of_pixels like 5,
                                      Number_of_pixels_horizontally like 5, Number_of_pixels_vertically like 5,
                                      font_size_to_use_in_plot like 8, figure_size_to_use_in_plot like (30,15),
                                      directory_for_saved_pdf_files like 'path/',
                                      permit_overwriting_of_submit_directory like False)
                                      
        Note: Font and Figure size should be chosen such that the plot refresh speed is acceptable for monitoring
        A few useful sizes and combinations:
            1. Large :  Font Size = 8, Figure Size = (30,15)
            2. Medium:  Font Size = 6, Figure Size = (15,8)
            3. Small :  Font Size = 4, Figure Size = (10,6)
        '''
        rogue.interfaces.stream.Slave.__init__(self)
        self.hist_xranges = [toa_xrange, tot_xrange]
        self.hist_xbins = [toa_xbins, tot_xbins]
        self.xpixels, self.ypixels = xpixels, ypixels
        self.number_of_pixels = self.xpixels * self.ypixels

        self.data_array_list = [None]*2
        #self.data_array_list[0] = np.zeros((self.number_of_pixels,toa_xbins), dtype=int)
        #self.data_array_list[1] = np.zeros((self.number_of_pixels,tot_xbins), dtype=int)
        self.data_array_list[0] = []
        self.data_array_list[1] = []
        for i in range(self.number_of_pixels):
            self.data_array_list[0].append([])
            self.data_array_list[1].append([])
            
        self.hits_toa_array = np.zeros((ypixels,xpixels), dtype=int)
        self.hits_tot_array = np.zeros((ypixels,xpixels), dtype=int)
        plt.rcParams.update({'font.size': font_size})
#         plt.ion()

        self.fig = plt.figure(num=plot_title, figsize=fig_size, dpi=100)
        self.gs = gridspec.GridSpec(6, 16)
        
        self.hist_group_list = []
        grid_range = (self.gs[:3, :14], self.gs[4:, :14])
        titles = ('TOA', 'TOT Coarse')
        xtitles = ('TOA Discrete Units', 'TOTc Discrete Units')
        for hist_index in range(2):
            hist_group = self.fig.add_subplot(grid_range[hist_index])
            hist_group.set_title(titles[hist_index])
            hist_group.set_xlabel(xtitles[hist_index])
            hist_group.set_xlim( self.hist_xranges[hist_index][0], self.hist_xranges[hist_index][1] )
            for pixel_i in range(self.number_of_pixels):
                pixel_hist = hist_group.hist( self.data_array_list[hist_index][pixel_i], self.hist_xbins[hist_index], label=str(pixel_i), histtype = 'step' )
            if hist_index == 0: hist_group.legend(loc=(0.9,.2), ncol=2)
            hist_group.set_xticks( np.arange(self.hist_xranges[hist_index][0], self.hist_xranges[hist_index][1], 4) )
            hist_group.tick_params(which="minor", bottom=False, left=False)
            self.hist_group_list.append(hist_group)
        
        self.ax2 = self.fig.add_subplot(self.gs[4:7, 14:])
        self.ax2.set_title('TOA - Hits')
        self.ax2.set_xlabel('Column')
        self.ax2.set_ylabel('Row')
        self.im2 = self.ax2.imshow(self.hits_toa_array, aspect='equal', cmap='cividis')
        self.cbar2 = self.ax2.figure.colorbar(self.im2, ax=self.ax2, orientation='horizontal', aspect=20, pad=.15)
        self.cbar2.ax.set_ylabel("Scale")
        self.ax2.set_xticks(np.arange(self.xpixels))
        self.ax2.set_yticks(np.arange(self.ypixels))
        self.ax2.set_xticklabels(np.linspace(start=0,stop=self.xpixels-1,num=self.xpixels,dtype=int))
        self.ax2.set_yticklabels(np.linspace(start=0,stop=self.ypixels-1,num=self.ypixels,dtype=int))
        for edge, spine in self.ax2.spines.items():
            spine.set_visible(False)
        self.ax2.set_xticks(np.arange(self.xpixels+1)-.5, minor=True)
        self.ax2.set_yticks(np.arange(self.ypixels+1)-.5, minor=True)
        self.ax2.grid(which="minor", color="w", linestyle='-', linewidth=3)
        self.ax2.tick_params(which="minor", bottom=False, left=False)
        
        self.fig.tight_layout()
        self.fig.canvas.draw()
        plt.pause(0.000001)
        self.fig.canvas.flush_events()
        
    def reset(self):
        '''
        To reset, or zero out, the stored arrays that integrate the number of hits and TOT/TOA values recorded:
            myObject.reset()
        '''
        #self.data_array_list[0] = np.zeros((self.number_of_pixels,toa_xbins), dtype=int)
        #self.data_array_list[1] = np.zeros((self.number_of_pixels,tot_xbins), dtype=int)
        self.data_array_list[0] = []
        self.data_array_list[1] = []
        for i in range(self.number_of_pixels):
            self.data_array_list[0].append([])
            self.data_array_list[1].append([])

        self.hits_toa_array = np.zeros((self.ypixels,self.xpixels), dtype=int)
        self.refreshDisplay()
        

    def _acceptFrame(self,frame):
        snap=False 
        instant=False
        # First it is good practice to hold a lock on the frame data.
        with frame.lock():
            eventFrame = feb.ParseFrame(frame)

            hit_data = np.zeros(self.xpixels*self.ypixels, dtype=int)
            for i in range( len(eventFrame.pixValue) ):
                pixel = eventFrame.pixValue[i]
                #if ((pixel.TotData >>  2) & 0x7F) == 127:
                #   print( pixel.TotData, pixel.ToaOverflow, pixel.TotOverflow)
                if pixel.Hit and not pixel.ToaOverflow and not pixel.TotOverflow and pixel.ToaData != 0:

                    hit_data[pixel.PixelIndex] = pixel.Hit

                    hit_data_toa = pixel.ToaData
                    hit_data_totc = (pixel.TotData >>  2) & 0x7F
                    print()
                    print(self.data_array_list[0][pixel.PixelIndex])
                    print()
                    self.data_array_list[0][pixel.PixelIndex].append(hit_data_toa)
                    self.data_array_list[1][pixel.PixelIndex].append(hit_data_totc)
                    

            hits_toa_data_binary = np.reshape(hit_data, (self.ypixels,self.xpixels), order='F')
            self.hits_toa_array += hits_toa_data_binary


    def refreshDisplay(self):
        '''
        This function updates the plot with the new arrays. The comments can be uncommented if
        one wishes to establish a fixed number of tick marks on the various colorbars in the plot
        A copy of this function is made private to protect against changes from inheritance 
        
        the plt.pause() can be uncommented if one wishes to keep the plot constantly in the foreground
        '''
        print(self.data_array_list[0])
        for hist_index, hist_group in enumerate(self.hist_group_list):
            for pixel_i in range(self.number_of_pixels):
                pixel_hist = hist_group.hist( self.data_array_list[hist_index][pixel_i], self.hist_xbins[hist_index], label=str(pixel_i), histtype = 'step' )

        self.im2.set_data(self.hits_toa_array)
        self.cbar2.mappable.set_clim(vmin=np.amin(self.hits_toa_array),vmax=np.amax(self.hits_toa_array))
        self.cbar2.draw_all() 
        #self.fig.tight_layout()
        self.fig.canvas.draw()

        self.fig.canvas.flush_events()


    def test_fill( self, test_data ): #test_data = [(pixel_hits, toa_data, tot_data)]*25
        hit_data = np.zeros(self.xpixels*self.ypixels, dtype=int)
        for i in range( len(test_data) ):
            test_pixel = test_data[i]
            pix_index = test_pixel[0]
            if test_pixel[1]:
                hit_data[pix_index] = test_pixel[1]

                hit_data_toa = test_pixel[2]
                hit_data_totc = test_pixel[3]

                self.data_array_list[0][pix_index].append(hit_data_toa)
                self.data_array_list[1][pix_index].append(hit_data_totc)

        hits_toa_data_binary = np.reshape(hit_data, (self.ypixels,self.xpixels), order='F')
        self.hits_toa_array += hits_toa_data_binary

def test_run():
    event_display = beamTestEventDisplay( plot_title='Test Run', font_size=6, fig_size=(14,7) )

    while(True):
        fake_data = []
        for fake_pix_i in [3,7,12]: 
            fake_hit = random.randint(0,1)
            fake_toa = random.randint(0,127)
            fake_tot = random.randint(0,127)
            fake_data.append( (fake_pix_i, fake_hit,fake_toa,fake_tot) )
        event_display.test_fill(fake_data)
        event_display.refreshDisplay()
        time.sleep(1)

#test_run() #uncomment this line and run this file by itself to test
