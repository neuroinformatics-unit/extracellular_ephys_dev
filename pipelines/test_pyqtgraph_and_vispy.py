import sys
import pyqtgraph as pg
import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg

# SpikeInterface provides some CatGT-like functionality but does not
# capture all options, especially around gate and trigger concatenation.
# Implement a CatGT reader ourselves for this.

from pathlib import Path
import matplotlib.pyplot as plt

data_path = Path(r"C:\data\spike_interface\rawdata\1110925")
run_name = "1110925_test_shank1"

import spikeinterface.extractors as se
import spikeinterface.widgets as sw
import spikeinterface.preprocessing as spre
from spikeinterface.core import order_channels_by_depth
import spikeinterface.full as si  # TODO
import matplotlib

run_level_path = data_path / (run_name + "_g0")

rec = se.read_spikeglx(folder_path=run_level_path,
                             stream_id="imec0.ap",
                             all_annotations=True)

fs = rec.get_sampling_frequency()
start_t = int(25*fs)
stop_t = int(25.5*fs)

rec = spre.phase_shift(rec)
rec = spre.bandpass_filter(rec, freq_min=300, freq_max=6000)
rec = spre.common_reference(rec, operator="median", reference="global")

y = rec.get_traces(return_scaled=False, start_frame=start_t, end_frame=stop_t)
x = np.linspace(start_t, stop_t - 1/fs, y.shape[0])

order_f, order_r = order_channels_by_depth(recording=rec, dimensions=('x', 'y'))

y = y[:, order_f]
y = y[:, :]
y = (y - np.mean(y, axis=0)) / np.std(y, axis=0)

# mean_channel_std = np.mean(np.std(y, axis=0))
max_channel_amp = np.max(np.max(np.abs(y), axis=0))
vspacing = max_channel_amp * 1.5

class MyApp(QtWidgets.QWidget):
    def __init__(self, y):

        QtWidgets.QWidget.__init__(self)
        lay = QtWidgets.QVBoxLayout()
        self.setLayout(lay)
        self.glw = pg.PlotWidget(show=True)
        lay.addWidget(self.glw)

        self.generate_line_plot()
        self.generate_image()

        self.show_image()
        self.image_shown = True

    def swap_plots(self):
        if self.image_shown:
            self.remove_image()
            self.show_lineplot()
            self.image_shown = False
        else:
            self.remove_lineplot()
            self.show_image()
            self.image_shown = True

    def show_image(self):
        self.glw.addItem(self.img)

    def show_lineplot(self):
        for curve in self.curves:
            self.glw.addItem(curve)

    def remove_image(self):
        self.glw.removeItem(self.img)

    def remove_lineplot(self):
        for curve in self.curves:
            self.glw.removeItem(curve)

    def generate_line_plot(self):
        nPlots = y.shape[1]

        self.curves = []
        for idx in range(nPlots):
            curve = pg.PlotCurveItem()
            curve.setData(y[:, idx] - np.mean(y[:, idx]))   # TODO: so many todo, e.g. xaxis, axis limit, scaling, background
            curve.setPos(0, idx * vspacing)
            self.curves.append(curve)

    def generate_image(self):
        self.img = pg.ImageItem()
        self.img.setImage(y)

        cm = pg.colormap.getFromMatplotlib("RdBu") # matplotlib.cm.get_cmap("RdBu")
        cm.reverse()  # check si do this
        self.img.setColorMap(cm)


        image_width = y.shape[0]
        image_height = vspacing * y.shape[1]  # if x and y-scales are the same
        vertical_offset = image_height / y.shape[1]
        self.img.setRect(QtCore.QRectF(0, 0 - vertical_offset / 2, image_width, image_height))

    def keyPressEvent(self, e):
        if e.key() == QtGui.Qt.Key_Space:
            self.swap_plots()
        # super(QtWidgets.QWidget, self).keyPressEvent(e)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp(y)
    window.show()
    sys.exit(app.exec())