"""
# this is actually very inefficient because
# for each chain it needs to pp all the way up (e.g. (0), (0-1), (0-1-2), (0-1-2-3))
"""
from preprocess import preprocess
from sort import run_sorting
import numpy as np
from pathlib import Path
from quality import quality_check

base_path = Path(r"/ceph/neuroinformatics/neuroinformatics/scratch/ece_ephys_learning")
sub_name = "1110925"
run_name = "1110925_test_shank1"

output_path = base_path / "derivatives" / sub_name / f"{run_name}_g0"  # TODO: handle internally when gates / triggers method decided.

quality_check(output_path,
              sorter="kilosort2_5")

