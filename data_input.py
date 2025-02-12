import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from scipy.signal import butter, lfilter
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

class EEGPlotter:
    def __init__(self, port='COM6', sampling_rate=250, window_size=5):
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
        
        # Setup Plot
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(title='Live EEG Data')
        self.win.show()
        self.plots = []
        self.curves = []
        for i in range(self.num_channels):
            p = self.win.addPlot(row=i, col=0)
            p.setYRange(-100, 100)
            curve = p.plot()
            self.plots.append(p)
            self.curves.append(curve)
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
            for i, ch in enumerate(self.channel_indices):
                filtered_data = self.bandpass_filter(data[ch])
                self.curves[i].setData(filtered_data)
    
    def run(self):
        QtWidgets.QApplication.instance().exec_()
        self.board.stop_stream()
        self.board.release_session()

if __name__ == '__main__':
    plotter = EEGPlotter()
    plotter.run()
