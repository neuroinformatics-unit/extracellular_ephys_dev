from swc_ephys.pipeline.preprocess import preprocess
from pathlib import Path
#import matplotlib
#matplotlib.use('tkagg')
import matplotlib.pyplot as plt
import spikeinterface as si
import pandas as pd
import numpy as np
from scipy import ndimage
from scipy import stats

traces = pd.read_csv(r"C:\fMRIData\git-repo\extracellular_ephys_dev\test_data.csv")

traces = traces.to_numpy()

def plot_traces(traces):
    plt.imshow(traces.T,  aspect='auto', cmap="RdBu", origin="lower", interpolation="nearest")
    plt.show()

traces = traces[0:500, :]

plot_traces(traces)


# could spline interpolate before!
traces_work = traces - np.mean(traces, axis=0)
# traces = traces / np.std(traces, ddof=1, axis=0)
traces_work = ndimage.filters.gaussian_filter(traces_work, sigma=1)

# plot_traces(traces)

low, high = np.percentile(traces_work.ravel(), (10, 90))
print(low, high)
cut_range = traces_work.ravel()[np.where(np.logical_and(traces_work.ravel() > low, traces_work.ravel() < high))]


mean = np.mean(cut_range)
std = np.std(cut_range, ddof=1)

norm = stats.norm(mean, std)

traces_prob = np.empty(traces_work.shape)
traces_prob.fill(np.nan)

n = 10  # only even numbers allowed
for col in range(traces_work.shape[1]):
    print(col)
    for row in range(traces_work.shape[0]):

        if row - int(n / 2) <= 0:
            local_samples = traces_work[0:n, col]
        elif traces_work.shape[0] - (row + int(n / 2)) <= 0:
            local_samples = traces_work[traces_work.shape[0] - n:traces_work.shape[0], col]  # note this int rounds, note this is n/2:n/2-1
        else:
            local_samples = traces_work[row - int(n / 2): row + int(n / 2), col]

        traces_prob[row, col] = np.sum(norm.logpdf(local_samples)) / n  # shit this takes ages!

plot_traces(traces_prob)

x = 1 / np.abs(traces_prob)
x = x / np.median(x)
x[x>1] = 1

traces -= traces * x
plot_traces(traces)


# interesting
if False:
    for t in range(traces.shape[0]):
        plt.hist(traces[t, :], bins=50)
        plt.show()



