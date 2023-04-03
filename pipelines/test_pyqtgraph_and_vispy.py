import sys
import pyqtgraph as pg
import numpy as np
from PySide6 import QtWidgets
import pyqtgraph as pg

# SpikeInterface provides some CatGT-like functionality but does not
# capture all options, especially around gate and trigger concatenation.
# Implement a CatGT reader ourselves for this.

from pathlib import Path
import matplotlib.pyplot as plt

data_path = Path(r"C:\data\spike_interface")
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
start_t = int(1000*fs)
stop_t = int(1005*fs)


rec = spre.bandpass_filter(rec, freq_min=300, freq_max=6000)
rec = spre.common_reference(rec, operator="median", reference="global")


y = rec.get_traces(return_scaled=True, start_frame=int(1000*fs), end_frame=int(1001*fs))
x = np.linspace(start_t, stop_t - 1/fs, y.shape[0])

order_f, order_r = order_channels_by_depth(recording=rec, dimensions=('x', 'y'))

y = y[:, order_f]
y = y - np.mean(y, axis=0)
y = y / np.std(y, axis=0)

mean_channel_std = np.mean(np.std(y, axis=0))
max_channel_amp = np.max(np.max(np.abs(y), axis=0))
vspacing = max_channel_amp * 1.5


HEAT = True

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        lay = QtWidgets.QVBoxLayout()
        self.setLayout(lay)
        self.glw = pg.PlotWidget(show=True)
        lay.addWidget(self.glw)

        if not HEAT:
            nPlots = y.shape[1]
            print(nPlots)

            self.curves = []
            for idx in range(nPlots):
                curve = pg.PlotCurveItem()
                curve.setData(y[:, idx] - np.mean(y[:, idx]))   # TODO: so many todo, e.g. xaxis, axis limit, scaling, background
                self.glw.addItem(curve)
                curve.setPos(0, idx * vspacing)
                self.curves.append(curve)

        else:

            img = pg.ImageItem()
            img.setImage(y)
            self.glw.addItem(img)

            cm = pg.colormap.getFromMatplotlib("RdBu") # matplotlib.cm.get_cmap("RdBu")

            img.setColorMap(cm)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())