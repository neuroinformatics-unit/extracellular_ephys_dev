from swc_ephys.pipeline.preprocess import preprocess
from pathlib import Path
#import matplotlib
#matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import spikeinterface as si
import pandas as pd

base_path = Path(r"C:\data\spike_interface")
sub_name = "1110925"
run_name = "1110925_test_shank1"

data = preprocess(base_path=base_path, sub_name=sub_name, run_name=run_name)

recording = data['3-raw-phase_shift-bandpass_filter-common_reference']
fs = recording.get_sampling_frequency()

traces = recording.get_traces(return_scaled=True, start_frame=int(200*fs), end_frame=int(200.5*fs))
forward, reverse = si.core.order_channels_by_depth(recording, dimensions=('x', 'y'))
traces = traces[:, forward]

def plot_traces(traces):
    plt.imshow(traces.T,  aspect='auto', cmap="RdBu", interpolation="nearest", origin="lower")
    plt.show()

plot_traces(traces)

pd.DataFrame(traces).to_csv(r"C:\fMRIData\git-repo\extracellular_ephys_dev\test_data.csv", index=None)