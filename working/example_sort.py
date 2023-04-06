"""
# this is actually very inefficient because
# for each chain it needs to pp all the way up (e.g. (0), (0-1), (0-1-2), (0-1-2-3))
"""
from preprocess import preprocess
from sort import run_sorting
import numpy as np
from pathlib import Path

base_path = Path(r"/ceph/neuroinformatics/neuroinformatics/scratch/ece_ephys_learning")
sub_name = "1110925"
run_name = "1110925_test_shank1"

data = preprocess(base_path=base_path,
                  sub_name=sub_name,
                  run_name=run_name)

if __name__ == "__main__":
    # sorting uses multiprocessing and so MUST
    # be run in __main__

    # TODO: this is probably doing crazy stuff with kilosorts pp??? need to check carefuly
    # the options KS is run with, and provide method to override ks settings
    run_sorting(data,  # TODO: this is stupid
                sorter="kilosort2_5")
