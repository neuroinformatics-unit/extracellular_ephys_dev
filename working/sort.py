from preprocess import preprocess
from visualise import visualise
import spikeinterface.sorters  as ss
import utils
import os
from pathlib import Path
import pickle
import spikeinterface as si

def run_sorting(data, # TODO: accept data object OR path to written binary
                sorter="kilosort2_5"
                ):
    """
    # if data, we need to pass the last recording in the preprocessing chain
    # to run_sorter. First, we save in SI format (otherwise, run_sorter saves
    # as less accessible binary with no metadata I can see). Then
    # run sorting (SI SHOULD TODO) will know the fp for the saved recording
    # already( TODO>!>!>)., Otherwise, if a str is passed, used the
    # previously saved recording.
    """
    # TODO: rework file output
    # have an option to save intermediate data, or can delete and just run full chain through

    supported_sorters = ["kilosort2", "kilosort2_5", "kilosort3"]
    assert sorter in supported_sorters, f"sorter must be: {supported_sorters}"

    if isinstance(data, str) or isinstance(data, Path):
        utils.message_user(f"\nLoading binary preprocessed data from {data}\n")
        data, recording = utils.load_data_and_recording(data)
    else:
        utils.message_user(f"\nSaving data class and binary preprocessed data to {data.preprocessed_binary_data_path}\n")  # OMD fix this reuse TODO DONT MIX PRINT AND FUNCTINOLAL LOGIC!!
        data.save_all_preprocessed_data()
        recording, __ = utils.get_dict_value_from_step_num(data, "last")

    data.set_sorter_output_paths(sorter)

    # this must be run from the folder that has both sorter output AND
    # rawdata
    os.chdir(data.base_path)

    utils.message_user(f"Starting {sorter} sorting...")
    sorting_output = ss.run_sorter(sorter,
                                   recording,
                                   output_folder=data.sorter_output_path,
                                   singularity_image=get_sorter_path(sorter))

    # TODO: dump some kind of config with data configs in the sorter output too
    utils.message_user(f"Saving sorter output to {data.sorter_output_path}")
    sorting_output.save(folder=data.sorter_output_path)


def get_sorter_path(sorter):
    """
    TODO: these should be loaded on a module.
    This is NOT good!
    """
    base_path = Path("/ceph/neuroinformatics/neuroinformatics/scratch/sorter_images")
    return base_path / sorter / f"{sorter}-compiled-base.sif"