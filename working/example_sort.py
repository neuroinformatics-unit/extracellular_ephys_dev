from preprocess import preprocess
from visualise import visualise
import spikeinterface.sorters  as ss
import utils

base_path = r"/ceph/neuroinformatics/neuroinformatics/scratch/ece_ephys_learning"
sub_name = "1110925"
run_name = "1110925_test_shank1"
import os

# def run_sorting(data,
#                 sorter,
#                 output_folder=data.)

if __name__ == "__main__":

    data = preprocess(base_path=base_path,
                      sub_name=sub_name,
                      run_name=run_name)

    data.set_sorter_output_path()

    rec, __ = utils.get_dict_value_from_step_num(data, "last")

    # this must be run from the folder that has both sorter output AND
    # rawdata
    os.chdir(base_path)

    sorting_output = ss.run_sorter("kilosort2_5",
                                    rec,
                                    output_folder=data.sorter_output_path,
                                    singularity_image=True)

    # dump some kind of config with data configs in the sorter output too

    sorting_output.save(folder=data.sorter_output_path)
