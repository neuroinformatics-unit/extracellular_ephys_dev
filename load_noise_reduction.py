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
from scipy import signal

traces = pd.read_csv(r"C:\fMRIData\git-repo\extracellular_ephys_dev\test_data.csv")

traces = traces.to_numpy()

def plot_traces(traces):
    # plt.imshow(traces.T[:150, :4000],  aspect='auto', cmap="RdBu", origin="lower", interpolation="nearest")
    plt.plot(traces.T[40, :2000])
    plt.show()

# traces = traces[0:500, :]

# plot_traces(traces)


# could spline interpolate before!
traces_work = traces - np.mean(traces, axis=0)
# traces = traces / np.std(traces, ddof=1, axis=0)
traces_work = ndimage.filters.gaussian_filter(traces_work, sigma=1)

plot_traces(traces)

low, high = np.percentile(traces_work.ravel(), (10, 90))
print(low, high)
cut_range = traces_work.ravel()[np.where(np.logical_and(traces_work.ravel() > low, traces_work.ravel() < high))]


mean = np.mean(cut_range)
std = np.std(cut_range, ddof=1)

norm = stats.norm(mean, std)

traces_prob = np.empty(traces_work.shape)
traces_prob.fill(np.nan)

n = 10

traces_prob = -(traces_work - mean)**2 / (2 * std**2)
traces_prob = signal.convolve2d(traces_prob, np.ones((n, 1)), mode="same")

transform_prob = np.log(np.abs(traces_prob))
demean_transform_prob = transform_prob - np.mean(transform_prob.ravel())

x = np.linspace(np.min(demean_transform_prob.ravel()), np.max(demean_transform_prob.ravel()), 1000)

top = 4  # cool this has to be even
s = np.std(demean_transform_prob.ravel()) / 1.5
y = np.exp((-(x - np.mean(demean_transform_prob.ravel()))**top) / (2 * s**top))  # (1 / np.sqrt(2 * np.pi * s**2)) *
y = y / np.max(y)

plt.plot(x, y)
plt.hist(demean_transform_prob.ravel(), density=True, bins=1000)
plt.show()

x = demean_transform_prob
y = np.exp((-(x - np.mean(demean_transform_prob.ravel()))**top) / (2 * s**top))  # (1 / np.sqrt(2 * np.pi * s**2)) *
y = y / np.max(y)

# subtraction method
plot_traces(traces - traces * y)

# scale method (less robust)
plot_traces(traces * 10**(1 - y))

# interesting
if False:
    for t in range(traces.shape[0]):
        plt.hist(traces[t, :], bins=50)
        plt.show()



