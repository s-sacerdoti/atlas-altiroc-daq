import datetime
import rogue
import collections
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
matplotlib.use('QT5Agg')
import os
import common as feb


class onlineEventDisplay1D(rogue.interfaces.stream.Slave):
    def refresh_histograms(self):
        self.ax0.cla()
        self.ax0.hist(**self.toa_plot_info)
        self.ax0.title.set_text('TOA')
        self.ax0.grid(linewidth=1)
        self.ax0.tick_params(which="minor", bottom=False, left=False)
        self.ax0.set_xticks( np.arange(0,self.toa_max,10) )

        self.ax1.cla()
        self.ax1.hist(**self.totc_plot_info)
        self.ax1.title.set_text('TOTc')
        self.ax1.grid(linewidth=1)
        self.ax1.tick_params(which="minor", bottom=False, left=False)
        self.ax1.set_xticks( np.arange(0,self.toa_max,10) )

        self.ax3.cla()
        self.ax3.set_title('Trigger Rate')
        self.ax3.plot(*self.trigger_rates)
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Rate (Hz)')

    

    def __init__(self, plot_title='Live Display', font_size=6, fig_size=(15,8),
                 toa_max=128, totc_max=128, xpixels=5, ypixels=5, num_bins=128, pixel_enable_list=range(25) ):
        rogue.interfaces.stream.Slave.__init__(self)

        self.xpixels, self.ypixels = xpixels, ypixels
        self.toa_max, self.totc_max = toa_max, totc_max
        self.num_channels = xpixels*ypixels
        self.num_bins = num_bins

        self.toa_array = np.zeros((self.num_bins,self.num_channels), dtype=int)
        self.totc_array = np.zeros((self.num_bins,self.num_channels), dtype=int)
        self.hit_array = np.zeros((self.ypixels,self.xpixels), dtype=int)
        plt.rcParams.update({'font.size': font_size})

        self.fig = plt.figure(num=plot_title, figsize=fig_size, dpi=100)
        self.gs = gridspec.GridSpec(6, 16)
        
        self.ax0 = self.fig.add_subplot(self.gs[:3, :13])
        self.toa_plot_info = {
            'x': np.array( [np.linspace(0,toa_max,num_bins,0)]*self.num_channels ).transpose()
          , 'weights': self.toa_array
          , 'histtype': 'step'
          , 'bins': self.num_bins
          , 'range': (0,toa_max)
          , 'linewidth': 2
          , 'label': [ str(i) for i in range(self.num_channels) ]
        }

        self.ax1 = self.fig.add_subplot(self.gs[3:, :13])
        self.totc_plot_info = {
            'x': np.array( [np.linspace(0,totc_max,num_bins,0)]*self.num_channels ).transpose()
          , 'weights': self.totc_array
          , 'histtype': 'step'
          , 'bins': self.num_bins
          , 'range': (0,totc_max)
          , 'linewidth': 2
          #, 'label': ('Signal', 'Background')
        }

        self.ax2 = self.fig.add_subplot(self.gs[4:, 13:])
        self.ax2.set_title('TOA - Hits')
        self.ax2.set_xlabel('Column')
        self.ax2.set_ylabel('Row')
        self.im2 = self.ax2.imshow(self.hit_array, aspect='equal', cmap='cividis')
        self.cbar2 = self.ax2.figure.colorbar(self.im2, ax=self.ax2, aspect=20, pad=.15)
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

        self.num_times_to_average = 10
        self.time_conversion = 6.25 # nano-seconds per timing-data unit
        num_rates_to_plot = 100
        self.timing_data = collections.deque([], self.num_times_to_average*2)
        self.trigger_rates = [ collections.deque([], num_rates_to_plot), collections.deque([], num_rates_to_plot) ]
        self.ax3 = self.fig.add_subplot(self.gs[2:4, 13:])

        self.refresh_histograms()

        handles, labels = self.ax0.get_legend_handles_labels()
        self.legend_ax = self.fig.add_subplot(self.gs[:2, 13:])
        self.legend_ax.legend(handles[::-1], labels[::-1], ncol=3, loc='upper left')
        self.legend_ax.axis('off')
        
        self.fig.tight_layout()
        self.fig.canvas.draw()
        plt.pause(0.000001)
        self.fig.canvas.flush_events()
        
    # Resets the stored arrays that integrate the number of hits and TOT/TOA values recorded
    def reset(self):
        self.toa_array.fill(0)
        self.totc_array.fill(0)
        self.hit_array = np.zeros((self.ypixels,self.xpixels), dtype=int)
        self.refreshDisplay()
    

    def _acceptFrame(self,frame):
        # First it is good practice to hold a lock on the frame data.
        with frame.lock():
            eventFrame = feb.ParseFrame(frame)

            hit_data = np.zeros(self.xpixels*self.ypixels, dtype=int)
            toa_list = []
            totc_list = []
            self.timing_data.append(eventFrame.Timestamp)
            for i in range( len(eventFrame.pixValue) ):
                pixel = eventFrame.pixValue[i]
                if pixel.Hit and not pixel.ToaOverflow:
                    toa = pixel.ToaData
                    totc = (pixel.TotData >>  2) & 0x7F
                    if pixel.PixelIndex > 14:
                        totc = (pixel.TotData >>  3) & 0x3F

                    toa_bin = int( toa * (self.toa_max/len(self.toa_array)) )
                    totc_bin = int( totc * (self.totc_max/len(self.totc_array)) )
                    self.toa_array[toa_bin][pixel.PixelIndex] += 1
                    self.totc_array[totc_bin][pixel.PixelIndex] += 1

                    hit_data[pixel.PixelIndex] = pixel.Hit

            hits_data_binary = np.reshape(hit_data, (self.ypixels,self.xpixels), order='F')
            self.hit_array += hits_data_binary


    def refreshDisplay(self):
        if len(self.timing_data) >= self.num_times_to_average:
            time1 = self.timing_data[-1] * self.time_conversion
            time0 = self.timing_data[-self.num_times_to_average] * self.time_conversion
            averaged_trigger_rate = self.num_times_to_average / (time1 - time0) # GHz frequency of triggers
            self.trigger_rates[0].append(time1 / 1E9) # seconds
            self.trigger_rates[1].append(averaged_trigger_rate * 1E9) # Hz
        self.refresh_histograms()

        self.im2.set_data(self.hit_array)
        self.cbar2.mappable.set_clim(vmin=np.amin(self.hit_array),vmax=np.amax(self.hit_array))
        self.cbar2.draw_all() 

        self.fig.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
