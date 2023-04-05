from preprocess import preprocess
from visualise import visualise
import spikeinterface.sorters  as ss
import utils
import os


def run_sorting(data,
                sorter="kilosort2_5"
                ):
    """
    """
    data.set_sorter_output_path()

    rec, __ = utils.get_dict_value_from_step_num(data, "last")

    # this must be run from the folder that has both sorter output AND
    # rawdata
    os.chdir(data.base_path)

    sorting_output = ss.run_sorter(sorter,
                                   rec,
                                   output_folder=data.sorter_output_path,
                                   singularity_image=True)

    # dump some kind of config with data configs in the sorter output too
    sorting_output.save(folder=data.sorter_output_path)