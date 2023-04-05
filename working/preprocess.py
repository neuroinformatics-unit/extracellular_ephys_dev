import spikeinterface.extractors as se
import spikeinterface.preprocessing as spre
import numpy as np
import json
from pathlib import Path
import utils
from collections import UserDict
from collections.abc import ItemsView, KeysView, ValuesView

# 1) for now assume spikeglx data
# 2) assume all gate, trigger, probe number are zero for now.
# Need to handle gate,trigger explicitly checking SI due to concatenation requirements
# probe number only requires iterating across user-passed probe numbers

pp_funcs = {"phase_shift": spre.phase_shift,
            "bandpass_filter": spre.bandpass_filter,
            "common_reference": spre.common_reference
            }

class Data(UserDict):
    def __init__(self, base_path, sub_name, run_name, pp_steps):
        super(Data, self).__init__({})  # TODO

        self.base_path = Path(base_path)
        self.rawdata_path = self.base_path / "rawdata"

        assert self.rawdata_path.is_dir(), "raw data must be in a folder rawdata that resides within base_path"

        self.sub_name = sub_name
        self.run_name = run_name
        self.run_level_path = None  # get with gate
        self.sorter_output_path = None

        self.pp_steps = pp_steps
        self.data = {"0-raw": None}
        self.opts = {"0-raw": None}  # sanity check for testing, is set in a extra loop

    def keys(self) -> KeysView:
        return self.data.keys()

    def items(self) -> ItemsView:
        return self.data.items()

    def values(self) -> ValuesView:
        return self.data.values()

    def set_sorter_output_path(self):
        assert self.run_level_path is not None, "must set run_level_path before sorter_output_path"
        self.sorter_output_path = self.base_path / "derivatives" / "sorting" / self.run_level_path.relative_to(self.rawdata_path)

def preprocess(base_path, sub_name, run_name, pp_steps=None):
    """
    TODO: currently only supports one subject. Easy to add more, accept list
    of sub names or search string. then add iterator over saving the data as so.

    handle all file searching operations
    TODO: fixed gate = 0
     # TODO: need to handle raw_data as top level path
    """
    if not pp_steps:
        pp_steps = {"1": ["phase_shift", {}],
                    "2": ["bandpass_filter", {"freq_min": 300, "freq_max": 6000}],
                    "3": ["common_reference", {"operator": "median", "reference": "global"}]
                   }

    checked_pp_steps, pp_step_names = check_and_sort_pp_steps(pp_steps)

    data = Data(base_path, sub_name, run_name, pp_steps)

    data.run_level_path = data.rawdata_path / sub_name / (run_name + "_g0")

    data["0-raw"] = se.read_spikeglx(folder_path=data.run_level_path, stream_id="imec0.ap", all_annotations=True)

    for step_num, pp_info in checked_pp_steps.items():

        perform_preprocessing_step(step_num, pp_info, data, pp_step_names)

    handle_bad_channels(data)
    return data


def handle_bad_channels(data):
    """
    """
    # good Q should BD detection be before or after pp?
    # good Q should BD detection be before or after pp?
    # good Q should BD detection be before or after pp?
    # good Q should BD detection be before or after pp?
    # good Q should BD detection be before or after pp?
    bad_channels = spre.detect_bad_channels(data["0-raw"])  # good Q should BD detection be before or after pp?

    message_user(f"The following channels were detected as dead / noise: {bad_channels[0]}\n"
                 f"TODO: DO SOMETHING BETTER WITH THIS INFORMATION. SAVE IT SOMEHWERE\n"
                 f"You may like to automatically remove bad channels by setting XXX as a preprocessing option\n"
                 f"TODO: check how this is handled in SI")


def perform_preprocessing_step(step_num, pp_info, data, pp_step_names):
    """
    """
    pp_name, pp_options = pp_info

    last_pp_step_output, __  = utils.get_dict_value_from_step_num(data,
                                                                  step_num=str(int(step_num) - 1))  # TODO: check annotation at this point

    new_name = f"{step_num}-" + "-".join(["raw"] + pp_step_names[:int(step_num)])

    assert pp_funcs[pp_name].__name__ == pp_name, "something is wrong in func dict"

    data[new_name] = pp_funcs[pp_name](last_pp_step_output, **pp_options)
    data.opts[new_name] = pp_options


def check_and_sort_pp_steps(pp_steps):
    """
    TODO: TEST THOROUGHLY!
    """
    sorted_pp_steps = {k:pp_steps[k] for k in sorted(pp_steps.keys())}

    # check keys
    assert all(key.isdigit() for key in sorted_pp_steps.keys()), "pp_steps keys must be integers"

    key_nums = [int(key) for key in sorted_pp_steps.keys()]

    assert np.min(key_nums) == 1, "dict keys must start at 1"

    diffs = np.diff(key_nums)
    assert np.unique(diffs).size == 1, "all dict keys must increase in steps of 1"
    assert diffs[0] == 1, "all dict keys must increase in steps of 1"

    # key names
    pp_step_names = [item[0] for item in sorted_pp_steps.values()]
    canonical_step_names = list(pp_funcs.keys())

    for user_passed_name in pp_step_names:
        assert user_passed_name in canonical_step_names, \
            f"{user_passed_name} not in allowed names: ({canonical_step_names}"

    # check options... or better (?), validate a config file.

    message_user(f"The preprocessing options dictionary is "
                 f"{json.dumps(sorted_pp_steps, indent=4, sort_keys=True)}")

    return sorted_pp_steps, pp_step_names


def message_user(message):
    """
    """
    print(message)
