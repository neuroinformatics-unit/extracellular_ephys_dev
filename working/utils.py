import numpy as np
from pathlib import Path
import pickle

def get_keys_first_char(dict_, as_int=False):
    # horrible?
    if as_int:
        return [int(key[0]) for key in dict_.keys()]
    else:
        return [key[0] for key in dict_.keys()]

def get_dict_value_from_step_num(dict_, step_num):

    if step_num == "last":
        pp_key_nums = get_keys_first_char(dict_, as_int=True)
        step_num = str(int(np.max(pp_key_nums)))  # for now, complete overkill but this is critical
        assert int(step_num) == len(dict_.keys()) - 1, "the last key has been taken incorrectly"

    pp_key = [key for key in dict_.keys() if key[0] == step_num]

    assert len(pp_key) == 1, "pp_key must always have unique first char "

    full_key = pp_key[0]

    return dict_[full_key], full_key

def message_user(message):
    """
    """
    print(message)

def load_data_and_recording(preprocessed_output_path):
    """
    """
    with open(Path(preprocessed_output_path) / "data_class.pkl", "rb") as file:  # TODO: think about type, enforce higher
        data = pickle.load(file)
    recording = data.load_preprocessed_binary()

    return data, recording