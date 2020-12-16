"""
utils.pyt
Claudia Espinoza, claudia.espinoza@meduniwien.ac.at

Created: 10:19 AM 12/16/2020

1. isis =  function to calculate iinterstimulus intervals
2. spike filter =  it filters the responses according to a stimulus, eg reward, TTL laser

It can be used after loading the spikes with the reader.py
It assumes sampliong rate of 20.000 Hz

Example:
>>> from fleximaus import utils as us
>>> myexp = us.SpikeFilter() --> Classify the spikes of a single cluster according to a specific stimuli

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def isis(spike_times, neuron_idx):
    """
    Compute a vector of interstimulus intervals (ISIs) for a single neuron given spike times.
    Args:
    spike_times (list of 1D arrays): Spike time dataset, with the first
      dimension corresponding to different neurons.
    neuron_idx (int): Index of the unit to compute ISIs for.

    Returns:
    isis (1D array): Duration of time between each spike from one neuron.
    """
    # Extract the spike times for the specified neuron
    single_neuron_spikes = spike_times[neuron_idx]

    # Compute the ISIs for this set of spikes
    isis = np.diff(single_neuron_spikes)
    return isis

class SpikeFilter(object):
    """
    It filter spikes according to stimuli
    e.g reward or a optogenetic stimulus

    """
    def __init__(self, stims, cluster, start, end):
        """
        stims (s) = Times in seconds for stimuli triggers. Set as a numpy array 
        cluster (s) = a sorted spike cluster. It is a numpy array
        It consider a sampling rate of 20 KHz --> sr  
        """
        sr = 20_000 # sampling rate
        self.stims = stims / sr
        self.cluster = cluster / sr
        self.start = start 
        self.end = end  
 
    def raster(self):
        """  
        #Creating a raster file
        """
        raster_stm = dict()
        for stm in self.stims:
            rast_spikes = [(spk-stm) for spk in self.cluster if spk > stm-self.start and spk < stm + self.end]
            raster_stm [stm] = rast_spikes
        
        return raster_stm

    def histogram(self, bin_size):
        """
        Generates an histogram of the restirazed spikes
        bin size tested = 0.005
        """  
        # 2. generates the histogram
        bins = [round(i,3) for i in np.arange(-self.start, self.end + 0.01, bin_size)]

        hist = dict()
        for i in bins:
            hist[i] = 0 
        
        raster = self.raster()
        for val in raster.values():
            for spk in val:
                for bn in bins:
                    if spk > bn and spk < round(bn+ bin_size, 3):
                        hist[round(bn+bin_size,3)] += 1 
        return hist
    
    def ins_FR(self, bin_size):
        """
        Output a data frame with information to calculate instanteneous firing rate (FR)
        in binning data.
        Columns are the firing frequency per bin plus 'ave','std','sterr' and 'bin start'.
        E.g Each columns has the FR in a bin size of 500 ms (check column['bins'])
        Rows are the stimulus     
        """
        # Returns a dictionary with the stimulus key, each contaning a subdictionary with 
        # bins as a key and and spike per bins divided by the bin size (time --> frequency) as value
        raster = self.raster()
        bins = [round(i,3) for i in np.arange(-self.start, self.end+0.01, bin_size)]
    
        FR_dic = dict()
        for stm in raster.keys():
            FR_dic[stm] = dict()
            for bn in bins:
                temp = 0
                for spk in raster[stm]:
                    if spk > bn and spk < round(bn+bin_size, 3):
                        temp += 1
                FR_dic[stm].update({bn:temp/bin_size})  # 1 spike per bin gives 200 Hz if the size is 0.05 ms

        # Create a data frame
        FR = pd.DataFrame()
        for i in FR_dic.keys():
            FR[i] = FR_dic[i].values()
        FR['ave'] = np.mean(FR, axis=1)
        FR['std'] = np.std(FR, axis=1)
        FR['sterr'] = np.std(FR, axis=1)/np.sqrt(len(FR.columns))
        FR['bins'] = bins
    
        return FR
    
    def plot_PSH(self, bin_size):
        """
        Quick plot of the rater, Histogram, FR
        Recommended bin size for plotting = 0.005
        """
        # variables for plotting
        rasterSeries = pd.Series(self.raster())
        hist = self.histogram(bin_size)
        FR = self.ins_FR(bin_size)
        
        #Setting the plot parameters
        
        fig,ax = plt.subplots(3, 1, figsize = (5,4), sharex = True, sharey = False)
        ax[0].eventplot(rasterSeries,color = 'indianred', lw= 1);  
        ax[0].spines['left'].set_visible(True)
        ax[0].spines['bottom'].set_visible(True)
        ax[0].set_ylabel('trials');
        
        ax[1].bar(hist.keys(),hist.values(), width=0.01, label = 'hist', color = 'indianred')
        ax[1].set_ylabel('spikes\n per bin');
        
        ax[2].plot(FR['bins'], FR['ave'], color = 'brown')
        ax[2].fill_between(FR['bins'],(FR['ave']+FR['sterr']),(FR['ave']-FR['sterr']),facecolor='black', alpha=0.5)
        ax[2].set_ylabel('FR');
        ax[2].set_xlabel('Time (s)');
        
        #plt.savefig('Cluster20.pdf')
        
        plt.show()