import datetime
import rogue
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
matplotlib.use('QT5Agg')
import os
import common as feb


class onlineEventDisplay(rogue.interfaces.stream.Slave):
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
    
    To update the plots and stored arrays with new data:
    myObject.update(1D_array_of_length=number_of_pixels_of_TOA_values, 
                    1D_array_of_length=number_of_pixels_of_TOT_values,
                    1D_array_of_pixel_indices_that_recorded_TOA_hit_not_overflow)
                    
    To update the plots and stored arrays with new data and take a snapshot of the current integrated plots
    after the new data has been added:
    myObject.update(1D_array_of_length=number_of_pixels_of_TOA_values, 
                    1D_array_of_length=number_of_pixels_of_TOT_values,
                    1D_array_of_pixel_indices_that_recorded_TOA_hit_not_overflow,
                    snap=True)
                    
    To update the plots and stored arrays with new data and take a snapshot of 
    only the instantaneous data from a single trigger event:
    myObject.update(1D_array_of_length=number_of_pixels_of_TOA_values, 
                    1D_array_of_length=number_of_pixels_of_TOT_values,
                    1D_array_of_pixel_indices_that_recorded_TOA_hit_not_overflow,
                    instant=True)
    '''
    def __init__(self, plot_title='Live Display', toa_xrange=(0,127), toa_yrange=(0,24), toa_xbins=128, toa_ybins=25, 
                 tot_xrange=(0,127), tot_yrange=(0,24), tot_xbins=128, tot_ybins=25, 
                 xpixels=5, ypixels=5, font_size=6, fig_size=(15,8), submitDir='./', overwrite=False):
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
        self.has_new_data = False
        self.toa_xrange, self.toa_yrange, self.toa_xbins, self.toa_ybins = toa_xrange, toa_yrange, toa_xbins,toa_ybins
        self.tot_xrange, self.tot_yrange, self.tot_xbins, self.tot_ybins = tot_xrange, tot_yrange, tot_xbins,tot_ybins
        self.xpixels, self.ypixels, self.submitDir, self.overwrite = xpixels, ypixels, submitDir, overwrite
        self.tot_binning_count = self.tot_xrange[1] / self.toa_xrange[1]

        if os.path.exists(self.submitDir):
            if not self.overwrite:
                raise OSError('Output directory {0:s}'.format(self.submitDir) + 
                              ' already exists. Either re-run with overwrite=True,'+ 
                              ' choose a different submitDir, or rm -rf it yourself.')
        else:
            try:
                os.makedirs(self.submitDir)
            except OSError:  
                print ("Creation of the directory %s failed" % self.submitDir)
            else:  
                print ("Successfully created the directory %s" % self.submitDir)
    
        self.toa_array = np.zeros((toa_ybins,toa_xbins), dtype=int)
        self.tot_array = np.zeros((tot_ybins,tot_xbins), dtype=int)
        self.tot_all_data = np.array([0])
        self.hits_toa_array = np.zeros((ypixels,xpixels), dtype=int)
        self.hits_tot_array = np.zeros((ypixels,xpixels), dtype=int)
        plt.rcParams.update({'font.size': font_size})
#         plt.ion()

        self.fig = plt.figure(num=plot_title, figsize=fig_size, dpi=100)
        self.gs = gridspec.GridSpec(6, 16)
        
        self.ax = self.fig.add_subplot(self.gs[:3, :14])
        self.ax.set_title('TOA')
        self.ax.set_xlabel('TOA Discrete Units')
        self.ax.set_ylabel('Pixel Number')
        self.im = self.ax.imshow(self.toa_array, aspect='auto')
        self.cbar = self.ax.figure.colorbar(self.im, ax=self.ax, orientation='horizontal', aspect=150, pad=.13)
        self.cbar.ax.set_ylabel("Scale")
        self.ax.set_xticks(np.arange(self.toa_xbins))
        self.ax.set_yticks(np.arange(self.toa_ybins))
        self.ax.set_xticklabels(np.linspace(start=self.toa_xrange[0],stop=self.toa_xrange[1],num=self.toa_xbins,dtype=int))
        self.ax.set_yticklabels(np.linspace(start=self.toa_yrange[0],stop=self.toa_yrange[1],num=self.toa_ybins,dtype=int))
        plt.setp(self.ax.get_xticklabels(), rotation=90, ha="right",
                 rotation_mode="anchor")
        for edge, spine in self.ax.spines.items():
            spine.set_visible(False)
        self.ax.set_xticks(np.arange(self.toa_xbins+1)-.5, minor=True)
        self.ax.set_yticks(np.arange(self.toa_ybins+1)-.5, minor=True)
        self.ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
        self.ax.tick_params(which="minor", bottom=False, left=False)
        
        self.ax2 = self.fig.add_subplot(self.gs[2:5, 14:])
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
        
        self.ax1 = self.fig.add_subplot(self.gs[3:, :14])
        self.ax1.set_title('TOT')
        self.ax1.set_xlabel('TOT Discrete Units')
        self.ax1.set_ylabel('Pixel Number')
        self.im1 = self.ax1.hist(self.tot_all_data, bins=np.arange(128))
        self.ax1.set_xticks(np.arange(128)-0.5) 
        #self.im1 = self.ax1.imshow(self.tot_array, aspect='auto')
        #self.cbar1 = self.ax1.figure.colorbar(self.im1, ax=self.ax1, orientation='horizontal', aspect=150, pad=.13)
        #self.cbar1.ax.set_ylabel("Scale")
        #self.ax1.set_yticks(np.arange(self.tot_ybins))
        #self.ax1.set_xticklabels(np.linspace(start=self.tot_xrange[0],stop=self.tot_xrange[1],num=self.tot_xbins,dtype=int))
        #self.ax1.set_yticklabels(np.linspace(start=self.tot_yrange[0],stop=self.tot_yrange[1],num=self.tot_ybins,dtype=int))
        #plt.setp(self.ax1.get_xticklabels(), rotation=90, ha="right",
        #         rotation_mode="anchor")
        #for edge, spine in self.ax1.spines.items():
        #    spine.set_visible(False)
        #self.ax1.set_xticks(np.arange(self.tot_xbins+1)-.5, minor=True)
        #self.ax1.set_yticks(np.arange(self.tot_ybins+1)-.5, minor=True)
        #self.ax1.grid(which="minor", color="w", linestyle='-', linewidth=1)
        #self.ax1.tick_params(which="minor", bottom=False, left=False)
        
        self.fig.tight_layout()
        self.fig.canvas.draw()
        plt.pause(0.000001)
        self.fig.canvas.flush_events()
        
    def reset(self):
        '''
        To reset, or zero out, the stored arrays that integrate the number of hits and TOT/TOA values recorded:
            myObject.reset()
        '''
        self.toa_array = np.zeros((self.toa_ybins,self.toa_xbins), dtype=int)
        self.tot_array = np.zeros((self.tot_ybins,self.tot_xbins), dtype=int)
        self.tot_all_data = np.array([0])
        self.hits_toa_array = np.zeros((self.ypixels,self.xpixels), dtype=int)
        self.refreshDisplay()
        
    def snapshot(self):
        '''
        This function is used to make a special call to the makeDisplay() that saves the current state of the plot
        to a pdf file in the same directory as the script
        '''
        self.__makeDisplay(self.toa_array, self.tot_array, self.hits_toa_array, 
                        "onlineEventDisplaySnapshot-{date:%Y-%m-%d__%H_%M_%S}".format(date=datetime.datetime.now()),
                          snap=True)
        
    def instantaneous(self, toa_data, tot_data, hits_toa_data, tot_all_data):
        '''
        This function is used to make a special call to the makeDisplay() that saves only the instantaneous
        TOa/TOT/Hit data to a pdf file in the same directory as the script
        '''
        self.__makeDisplay(toa_data, tot_data, hits_toa_data, 
                        "instantaneousEventDisplay-{date:%Y-%m-%d__%H_%M_%S}".format(date=datetime.datetime.now()),
                          snap=True)
    

    def _acceptFrame(self,frame):
        snap=False 
        instant=False
        # First it is good practice to hold a lock on the frame data.
        with frame.lock():
            eventFrame = feb.ParseFrame(frame)

            hit_data = np.zeros(self.xpixels*self.ypixels, dtype=int)
            for i in range( len(eventFrame.pixValue) ):
                pixel = eventFrame.pixValue[i]
                #if pixel.Hit and not pixel.ToaOverflow:
                if pixel.Hit:
                    hit_data[pixel.PixelIndex] = pixel.Hit
                    self.toa_array[pixel.PixelIndex][pixel.ToaData] += 1
                    #scale down tot data so we can use 128 bins for tot and toa
                    HitDataTOTc = (pixel.TotData >>  2) & 0x7F
                    tot_bin = int(HitDataTOTc/self.tot_binning_count)
                    self.tot_array[pixel.PixelIndex][tot_bin] += 1
                    if pixel.PixelIndex == 13 and HitDataTOTc != 127: 
                        self.tot_all_data = np.append(self.tot_all_data,HitDataTOTc)
            hits_toa_data_binary = np.reshape(hit_data, (self.ypixels,self.xpixels), order='F')
            self.hits_toa_array += hits_toa_data_binary
            print(self.tot_all_data)
        if(snap): self.snapshot()
        if(instant): self.instantaneous(toa_data_binary, tot_data_binary, hits_toa_data_binary)
        self.has_new_data = True


    def refreshDisplay(self):
        self.has_new_data = False
        self.__makeDisplay(self.toa_array, self.tot_array, self.hits_toa_array,self.tot_all_data)
        

    def makeDisplay(self, toa_data, tot_data, hits_toa_data, tot_all_data,figname="onlineEventDisplay", snap=False):
        '''
        This function updates the plot with the new arrays. The comments can be uncommented if
        one wishes to establish a fixed number of tick marks on the various colorbars in the plot
        A copy of this function is made private to protect against changes from inheritance 
        
        the plt.pause() can be uncommented if one wishes to keep the plot constantly in the foreground
        '''
        self.im.set_data(toa_data)
        print(tot_data[7])
        print(tot_all_data)
        self.im1 = plt.hist(tot_all_data, bins=np.arange(128))
        self.ax1.set_xticks(np.arange(128)-0.5) 
        #self.im1.set_data(tot_data)
        self.im2.set_data(hits_toa_data)
        self.cbar.mappable.set_clim(vmin=np.amin(toa_data),vmax=np.amax(toa_data))
        #self.cbar1.mappable.set_clim(vmin=np.amin(tot_data),vmax=np.amax(tot_data))
        self.cbar2.mappable.set_clim(vmin=np.amin(hits_toa_data),vmax=np.amax(hits_toa_data))
        self.cbar.draw_all() 
        #self.cbar1.draw_all() 
        self.cbar2.draw_all() 
        #self.fig.tight_layout()
        if(snap): self.fig.savefig(self.submitDir+"/"+ figname + ".pdf")
        self.fig.canvas.draw()
        #self.ax.draw_artist(self.im)
        #self.ax1.draw_artist(self.im1)
        #self.ax2.draw_artist(self.im2)
        #self.fig.canvas.update()

        self.fig.canvas.flush_events()

    __makeDisplay = makeDisplay
