"""
"""
import yaml
from quality import quality_check
from preprocess import preprocess
from sort import run_sorting
import yaml

def run_full_pipeline(base_path,
                      sub_name,
                      run_name,
                      preprocessing_config="test",
                      sorter="kilosort2_5"):
    """
    Must be run in main() as uses multiprocessing
    """
    pp_steps = {"1": ["phase_shift", {}],  # TODO: move
                "2": ["bandpass_filter", {"freq_min": 300, "freq_max": 6000}],
                "3": ["common_reference", {"operator": "median", "reference": "global"}]
                }


    with open(base_path, "w") as config_file:
        yaml.dump(pp_steps, config_file, sort_keys=False)

    breakopint()

    # Get the recording object. This is lazy - no preprocessing
    # done yet
    data = preprocess(base_path=base_path,
                      sub_name=sub_name,
                      run_name=run_name,
                      pp_steps=None)  # TO FULL IN

    # Run sorting. This will save the final preprocessing step
    # recording to disk prior to sorting.
    run_sorting(data,
                sorter="kilosort2_5")

    # will save spikeinterface 'waveforms' output (TODO: currently, this is large)
    # to the sorter output dir. Quality checks are run and .csv of checks
    # output in the sorter folder as quality_metrics.csv
    quality_check(output_path,
                  sorter="kilosort2_5")
