import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from scipy.signal import butter, lfilter
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import threading
import numpy as np
from PyQt5 import QtWidgets
import time
import sys

class EEGPlotter:
    def __init__(self, port='/dev/ttyUSB0', sampling_rate=250, window_size=5):
        self.sampling_rate = sampling_rate
        self.window_size = window_size  # seconds
        self.num_samples = self.sampling_rate * self.window_size
        self.params = BrainFlowInputParams()
        self.params.serial_port = port
        self.board = BoardShim(BoardIds.CYTON_BOARD, self.params)
        self.board.prepare_session()

        # Configure gain settings to 8 for all active channels
        for i in range(1, 9):
            self.board.config_board(f'x{i}040010X')

        self.board.start_stream()
        self.channel_indices = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD)
        self.num_channels = len(self.channel_indices)

        # Set up GUI Layout
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(title='BrainFlow EEG GUI')
        self.ts_plots = [self.win.addPlot(row=i, col=0, colspan=2, title=f'Channel {i+1}', labels={'left': 'uV'}) for i in range(self.num_channels)]
        self.fft_plot = self.win.addPlot(row=1, col=2, rowspan=4, title='FFT Plot', labels={'left': 'uV', 'bottom': 'Hz'})
        self.fft_plot.setLimits(xMin=1, xMax=125, yMin=0, yMax=1e7)
        self.waves_plot = self.win.addPlot(row=5, col=2, rowspan=4, title='EEG Bands', labels={'left': 'uV', 'bottom': 'EEG Band'})
        self.waves_plot.setLimits(xMin=0.5, xMax=5.5, yMin=0)
        waves_xax = self.waves_plot.getAxis('bottom')
        waves_xax.setTicks([list(zip(range(6), ('', 'Delta', 'Theta', 'Alpha', 'Beta', 'Gamma')))])

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

    def bandpass_filter(self, data, lowcut=1.0, highcut=50.0, order=5):
        nyq = 0.5 * self.sampling_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return lfilter(b, a, data)

    def update_plot(self):
        data = self.board.get_current_board_data(self.num_samples)
        if data.shape[1] >= self.num_samples:
            t_data = np.array([self.bandpass_filter(data[ch]) for ch in self.channel_indices])

            # Time-series plots
            for j in range(self.num_channels):
                self.ts_plots[j].clear()
                self.ts_plots[j].plot(pen='r').setData(t_data[j])

            # FFT Calculation
            sp = [np.abs(np.fft.fft(t_data[i])) for i in range(self.num_channels)]
            freq = np.fft.fftfreq(self.num_samples, 1.0 / self.sampling_rate)
            self.fft_plot.clear()
            for k in range(self.num_channels):
                self.fft_plot.plot(pen='b').setData(freq, sp[k])

            # EEG Bands
            eeg_bands = {'Delta': (1, 4), 'Theta': (4, 8), 'Alpha': (8, 12), 'Beta': (12, 30), 'Gamma': (30, 45)}
            eeg_band_fft = {}
            sp_bands = np.abs(np.fft.fft(t_data[0]))  # Use first channel
            freq_bands = np.fft.fftfreq(self.num_samples, 1.0 / self.sampling_rate)

            for band in eeg_bands:
                freq_ix = np.where((freq_bands >= eeg_bands[band][0]) & (freq_bands <= eeg_bands[band][1]))[0]
                eeg_band_fft[band] = np.mean(sp_bands[freq_ix])

            bg1 = pg.BarGraphItem(x=[1, 2, 3, 4, 5], height=[eeg_band_fft[band] for band in eeg_bands], width=0.6, brush='r')
            self.waves_plot.clear()
            self.waves_plot.addItem(bg1)

    def run(self):
        QtWidgets.QApplication.instance().exec_()
        self.board.stop_stream()
        self.board.release_session()

if __name__ == '__main__':
    plotter = EEGPlotter()
    plotter.run()
