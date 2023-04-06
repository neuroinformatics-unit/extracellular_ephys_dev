"""
https://spikeinterface.readthedocs.io/en/latest/modules/qualitymetrics.html for
details on methods

TODO: almost certainly want this sparse, this is huge (12GB for 10GB data).
https://spikeinterface.readthedocs.io/en/latest/modules_gallery/core/plot_4_waveform_extractor.html
"""

import spikeinterface as si
from spikeinterface import curation
import spikeinterface.exporters as se
from spikeinterface.extractors import KiloSortSortingExtractor
from pathlib import Path
import utils


def quality_check(output_path_,
                  sorter="kilosort2_5"):
    """
    """
    data, recording = utils.load_data_and_recording(output_path_ / "preprocessed")  # TODO: remove _
    data.set_sorter_output_paths(sorter)

    sorting = KiloSortSortingExtractor(folder_path=output_path_ / f"{sorter}-sorting" / "sorter_output",  # fix this somewhere probability utils or preprocess class
                                       keep_good_only=False)

    sorting_without_excess_spikes = curation.remove_excess_spikes(sorting, recording)  # TODO: this is required, what exactly is it doing?

    if not data.waveforms_output_path.is_dir():
        waveforms = si.extract_waveforms(recording, sorting_without_excess_spikes, folder=data.waveforms_output_path)
    else:
        waveforms = si.load_waveforms(data.waveforms_output_path)

    metrics = si.qualitymetrics.compute_quality_metrics(waveforms)
    metrics.to_csv(data.quality_metrics_pathoutput_path / "quality_metrics.csv")
