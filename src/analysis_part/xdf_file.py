import os
import mne
import pyxdf
import logging
import numpy as np
from math import ceil, floor
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class XDFFile:
    def __init__(self, path, verbose=None, freq=2048):
        logging.basicConfig(level=logging.INFO)  # Use logging.INFO to reduce output.
        fname = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', path))
        self.streams, self.fileheader = pyxdf.load_xdf(fname)
        self.freq = freq
        self.cut_EEG = None

        if verbose is True:
            print("Found {} streams:".format(len(self.streams)))

            for ix, stream in enumerate(self.streams):
                print("Stream {}: {} - type {} - uid {} - shape {} at {} Hz (effective {} Hz)".format(
                    ix + 1, stream['info']['name'][0],
                    stream['info']['type'][0],
                    stream['info']['uid'][0],
                    (int(stream['info']['channel_count'][0]), len(stream['time_stamps'])),
                    stream['info']['nominal_srate'][0],
                    stream['info']['effective_srate'])
                )
                if any(stream['time_stamps']):
                    print("\tDuration: {} s".format(stream['time_stamps'][-1] - stream['time_stamps'][0]))
            print("Done.")

        else:
            print(type(self.streams), len(self.streams), type(self.streams[0]), len(self.streams[0]))
            print(self.streams[1]["time_series"].shape)

        self.data_EEG = np.array(self.streams[1]["time_series"]).transpose()[1:33]

    def showEEG(self):
        biosemi_montage = mne.channels.read_montage('biosemi32')
        info = mne.create_info(ch_names=biosemi_montage.ch_names[:-3], sfreq=self.freq, ch_types="eeg", montage=biosemi_montage)

        raw = mne.io.RawArray(self.data_EEG, info)

        raw.plot(n_channels=33, scalings='auto', title='EEG', show=True, block=True)

    def showCutEEG(self):
        if self.cut_EEG is None:
            print("ERROR: cut is None")
            return

        biosemi_montage = mne.channels.read_montage('biosemi32')
        info = mne.create_info(ch_names=biosemi_montage.ch_names[:-3], sfreq=self.freq, ch_types="eeg", montage=biosemi_montage)

        raw = mne.io.RawArray(self.cut_EEG, info)

        raw.plot(n_channels=33, scalings='auto', title='EEG', show=True, block=True)

    def showET(self):
        self.data_ET = np.array(self.streams[0]["time_series"])
        
        # plt.plot(self.data_ET[:,0]+self.data_ET[:,2]/2, label='x', len(self.data_ET)/129.4153)
        # plt.plot(self.data_ET[:,1]+self.data_ET[:,3]/2, label='y', len(self.data_ET)/129.4153)
        plt.plot(np.arange(len(self.data_ET[:,0]))/(len(self.data_ET[:,0])/129.4153), (self.data_ET[:,0]+self.data_ET[:,2])/2, label='x')
        plt.plot(np.arange(len(self.data_ET[:,0]))/(len(self.data_ET[:,0])/129.4153), (self.data_ET[:,1]+self.data_ET[:,3])/2, label='y')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

        plt.show()

    def cutEEG(self, start, end):
        ech_start = floor(start*self.freq)
        ech_end = ceil(end*self.freq)

        self.cut_EEG = self.data_EEG[:,ech_start:ech_end]

    def saveCut(self, path):
        if self.cut_EEG is None:
            print("ERROR: cut is None")
            return

        np.save(path + ".npy", self.cut_EEG)

    def loadCut(self, path):
        if self.cut_EEG is None:
            print("ERROR: cut is None")
            return

        self.cut_EEG = np.load(path + ".npy")