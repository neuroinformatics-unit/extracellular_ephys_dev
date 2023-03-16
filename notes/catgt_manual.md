This is a collection of notes from CaGT helper docs, found [here](https://billkarsh.github.io/SpikeGLX/help/dmx_vs_gbl/dmx_vs_gbl/),
[here](https://github.com/billkarsh/CatGT/tree/main/Build), 
[here](https://billkarsh.github.io/SpikeGLX/help/syncEdges/Sync_edges/)
and [the readme](https://github.com/billkarsh/CatGT/tree/main/CatGT-win), which is html format so see _vendored to read.

#### What does CatGT do?

* concatenates files from gate and trigger output files (see gate and triggers).
* performs advanced preprocessing steps including
  * t_shift (multiplex correction, on by default)
  * common average referencing (-gblcar)
  * filtering (biquad filter [cool implementation](https://github.com/billkarsh/CatGT/blob/main/Build/Biquad.cpp)) or frequency domain butter ([I think here](https://github.com/billkarsh/CatGT/blob/e5ee644deb68666f8ad34496cae3347d9f9e6877/Build/Pass1.cpp)).
  * -gfix : threshold based artefact correction (replace large spikes with zeros)
  * -loccar : disc-based CAR to avoid averaging across AP (not widely used)
  * extract tables of sync pulse edges (for use in TShift)
  * extract tables of non-neural event times

The full CatGT workflow is:

```
1) Load data (I guess inlcuding any gate and trigger concatenation)
2) Apply any specified biquad (time domain)
3) Transform to frequency domain
4) TShift
5) Apply any specified Butterworth filtering
6) Transform back to time domain
7) Detect gfix transients for later file editing
8) Loccar, gblcar (AP-band only)
9) Write file
10) Apply gfix transient edits to file
```

#### t_shift 

Details on the multiplexing correction issue can be found in the [IBL white paper](https://www.internationalbrainlab.com/repro-ephys) (it was suggested originally by Olivier
prior to inclusion in CatGT).


