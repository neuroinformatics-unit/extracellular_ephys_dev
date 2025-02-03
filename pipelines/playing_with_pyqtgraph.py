import sys
import pyqtgraph as pg
import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg
import spikewrap as sw
from spikewrap.utils import _utils

# Raw dat a plot as heatmap or line plot in PyQtGraph.
# Use space to switch between plotting modes.

from pathlib import Path

sub_path = sw.get_example_data_path() / "rawdata" / "sub-001"
ses_name = "ses-001"

import spikeinterface.extractors as se
import spikeinterface.preprocessing as spre
from spikeinterface.core import order_channels_by_depth

session = sw.Session(
    sub_path,
    ses_name,
    "spikeglx",
)

session.preprocess("neuropixels+kilosort2_5", per_shank=True, concat_runs=True)

# This is the first run, first shank, final preprocessing step (spikewrap holds
# all intermediate preprocessing steps for visualisation if required).
# In future this should have a nice getter.
prepro_dict = session._runs[0]._preprocessed["0"]._data
preprocesed_recording, _ = _utils._get_dict_value_from_step_num(prepro_dict, "last")

# Get the raw data to plot
fs = preprocesed_recording.get_sampling_frequency()
start_t = int(0*fs)
stop_t = int(0.25*fs)

y = preprocesed_recording.get_traces(return_scaled=False, start_frame=start_t, end_frame=stop_t)
x = np.linspace(start_t, stop_t - 1/fs, y.shape[0])

order_f, order_r = order_channels_by_depth(recording=preprocesed_recording, dimensions=('x', 'y'))

y = y[:, order_f]
y = y[:, :]
y = (y - np.mean(y, axis=0)) / np.std(y, axis=0)

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