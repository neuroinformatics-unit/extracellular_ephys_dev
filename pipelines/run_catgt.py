"""
Running CatGT

See notes for settings.

Command Line -----------------------------------------------------------------------------------------------------------

Can run in CMD by a) installing CatGT folder b) adding folder to path then 3) calling e.g.:

CatGT -dir=D:\data\spike-interface\testing\steve\1110925 -run=1110925_lse_shank1 -g=0 -t=0 -prb_fld -t_miss_ok -ap -prb=0 -apfilter=butter,12,300,9000 -gfix=0.40,0.10,0.02 -dest=D:\data

running this in cmd will spawn as a separate process. Also it is convenient to use the runit.bat, this will hold on to
the cmd window until job execution.

Jennifer Colonell ------------------------------------------------------------------------------------------------------

Alternatively, Jennifer Colonell pipeline has a wrapper for this:

https://github.com/AllenInstitute/ecephys_spike_sorting

and the original Allen ephys (for OpenEphys):

https://github.com/jenniferColonell/ecephys_spike_sorting

The implementation:
1) scripts/helpers/run_one_probe.runOne(). Thie sets up the arguments (in a dict)
   and runs modules/catGT_helper/__main__.py. This basically puts together
   all arguments in a string and calls Popen with the string.
It then reads the log output and does some copying around with files.

"""

# ----------------------------------------------------------------------------------------------------------------------
# SpikeInterface
# ----------------------------------------------------------------------------------------------------------------------

# SpikeInterface provides some CatGT-like functionality but does not
# capture all options, especially around gate and trigger concatenation.
# Implement a CatGT reader ourselves for this.

from pathlib import Path
import matplotlib.pyplot as plt

data_path = Path(r"C:\data\spike_interface")
sorter_output_path = r"C:\data\spike_interface\sorter_output"
run_name = "1110925_test_shank1"
ks_path = r"C:\fMRIData\git-repo\Kilosort-2.5\Kilosort-2.5"
show_plots = False

import spikeinterface.extractors as se
import spikeinterface.widgets as sw
import spikeinterface.preprocessing as spre
from spikeinterface.core import order_channels_by_depth
import spikeinterface.full as si  # TODO
import spikeinterface.sorters  as ss

def custom_plot(recording, title):

    if show_plots:
        channel_ids = recording.get_channel_ids()

        order_f, order_r = order_channels_by_depth(recording=rec, dimensions=('x', 'y'))

        sw.plot_timeseries(recording,
                    #       channel_ids=channel_ids[order_f][40:60],
                           order_channel_by_depth=True,
                   #        time_range=(5, 1005),
                           return_scaled=True,
                           show_channel_ids=True)
        plt.title(title)
        plt.show()


# Load the data

run_level_path = data_path / (run_name + "_g0")

rec = se.read_spikeglx(folder_path=run_level_path,
                             stream_id="imec0.ap",
                             all_annotations=True)

# Check the probe map
if show_plots:
    si.plot_probe_map(rec, with_channel_ids=False)
    plt.show()

# Plot the raw timeseries
channel_ids = rec.get_channel_ids()
fs = rec.get_sampling_frequency()
num_chan = rec.get_num_channels()
num_seg = rec.get_num_segments()

custom_plot(rec, title="Raw data")

# To replicate CatGT, we can e.g.
# 1) phase shift
# 2) filter
# 3) CAR

# TSHIFT (Fourier domain, phase rotation)
def run_preprocessing():

    rec_shift = spre.phase_shift(rec)  # requires probe information

    custom_plot(rec_shift, title="Shifted Data")  # TODO: see if PyqtGraph or vispy backend is possible.

    # FILTER

    rec_shift_filt = spre.bandpass_filter(rec_shift, freq_min=300, freq_max=6000)

    custom_plot(rec_shift_filt, title="Filtered")

    # CAR

    rec_shift_filt_car = spre.common_reference(rec_shift_filt, operator="median", reference="global")

    custom_plot(rec_shift_filt_car, title="CAR")

    return rec_shift_filt_car


if __name__ == "__main__":
    recording = run_preprocessing()

    # ss.Kilosort2_5Sorter.set_kilosort2_5_path(ks_path)
    sorting_KS2_5 = ss.run_sorter("kilosort2_5", recording, output_folder=sorter_output_path, docker_image=True)
    sorting_KS2_5.save(folder=sorter_output_path)