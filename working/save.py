from preprocess import preprocess
import utils
from spikeinterface.core import order_channels_by_depth
import spikeinterface.widgets as sw

sub_dir = r"C:\data\spike_interface\raw_data"  # TODO: this interface can be swapped out to take datashuttle input
sub_str = None
run_name = "1110925_test_shank1"  # how is this usually handled per-sub?

sub_dir = Path(sub_dir)

if sub_str is None:
    sub_path = sub_dir.glob("*")

elif isinstance(sub_str, str):
    sub_path = sub_dir.glob(sub_str)

else:
    sub_path = [Path / sub_name for sub_name in sub_str]

for sub_path in subs:

    # TODO: write test against standard workflow.

    data, opt_record = preprocess(top_level_dir=sub_path,
                                  run_name=run_name)

    final_step, __ = utils.get_dict_value_from_step_num(data,
                                                        "last")

breakpoint()