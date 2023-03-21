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

Details on the multiplexing correction issue can be found in the [IBL white paper](https://www.internationalbrainlab.com/repro-ephys) (it was suggested originally by Olivier prior to inclusion in CatGT).

#### How to Call

There are a lot of possible options (See Appendix A for all). Key options are:

```
-dir=data_dir
-apfilter=Typ,N,Fhi,Flo  ;apply ap band-pass filter of given {type, order, corners(float Hz)}
-lffilter=Typ,N,Fhi,Flo  ;apply lf band-pass filter of given {type, order, corners(float Hz)}
-gblcar                  ;apply ap global CAR filter over all channels
-gfix=0.40,0.10,0.02     ;rmv ap artifacts: ||amp(mV)||, ||slope(mV/sample)||, ||noise(mV)||
-dest=path               ;alternate path for output files (must exist)
-out_prb_fld             ;if using -dest, create output subfolder per probe

[unsure]
-xa=0,0,2,3.0,4.5,25     ;extract pulse signal from analog chan (js,ip,word,thresh1(V),thresh2(V),millisec)
-xd=2,0,384,6,500        ;extract pulse signal from digital chan (js,ip,word,bit,millisec)
(see also inverted versions of above)
-no_auto_sync            ;disable the automatic extraction of sync edges in all streams
-supercat={dir,run_ga}   ;concatenate existing output files across runs (see ReadMe)

[not really required but important]
-loccar=2,8              ;apply ap local CAR annulus (exclude radius, include radius)
-no_tshift               ;DO NOT time-align channels to account for ADC multiplexing
```

for -g, -t (see full readme for nice code example):

```
CatGT can concatenate files together that come from the same run. That is, the files have the same base run_name, but may have differing g- and t-indices.

    Example -g=0 (or -g=0,0): specifies the single g-index 0.
    Example -t=5 (or -t=5,5): specifies the single t-index 5.
    Example -g=1,4: specifies g-index range [1,4] inclusive.
    Example -t=0,100: specifies t-index range [0,100] inclusive.
```

## CatGT README notes




## Appendix A: All CatGt Input arguments

```
Which streams:
-ni                      ;required to process ni stream
-ob                      ;required to process ob streams
-ap                      ;required to process ap streams
-lf                      ;required to process lf streams
-obx=0,3:5               ;if -ob process these Oneboxes
-prb_3A                  ;if -ap or -lf process 3A-style probe files, e.g. run_name_g0_t0.imec.ap.bin
-prb=0,3:5               ;if -ap or -lf AND !prb_3A process these probes

Options:
-no_run_fld              ;older data, or data files relocated without a run folder
-prb_fld                 ;use folder-per-probe organization
-prb_miss_ok             ;instead of stopping, silently skip missing probes
-gtlist={gj,tja,tjb}     ;override {-g,-t} giving each listed g-index its own t-range
-t=cat                   ;extract events from CatGT output files (instead of -t=ta,tb)
-exported                ;apply FileViewer 'exported' tag to in/output filenames
-t_miss_ok               ;instead of stopping, zero-fill if trial missing
-zerofillmax=500         ;set a maximum zero-fill span (millisec)
-startsecs=120.0         ;skip this initial span of each input stream (float seconds)
-maxsecs=7.5             ;set a maximum output file length (float seconds)
-apfilter=Typ,N,Fhi,Flo  ;apply ap band-pass filter of given {type, order, corners(float Hz)}
-lffilter=Typ,N,Fhi,Flo  ;apply lf band-pass filter of given {type, order, corners(float Hz)}
-no_tshift               ;DO NOT time-align channels to account for ADC multiplexing
-loccar=2,8              ;apply ap local CAR annulus (exclude radius, include radius)
-gblcar                  ;apply ap global CAR filter over all channels
-gfix=0.40,0.10,0.02     ;rmv ap artifacts: ||amp(mV)||, ||slope(mV/sample)||, ||noise(mV)||
-chnexcl={prb;chans}     ;this probe, exclude listed chans from ap loccar, gblcar, gfix
-xa=0,0,2,3.0,4.5,25     ;extract pulse signal from analog chan (js,ip,word,thresh1(V),thresh2(V),millisec)
-xd=2,0,384,6,500        ;extract pulse signal from digital chan (js,ip,word,bit,millisec)
-xia=0,0,2,3.0,4.5,2     ;inverted version of xa
-xid=2,0,384,6,50        ;inverted version of xd
-bf=0,0,8,2,4,3          ;extract numeric bit-field from digital chan (js,ip,word,startbit,nbits,inarow)
-inarow=5                ;extractor {xa,xd,xia,xid} antibounce stay high/low sample count
-no_auto_sync            ;disable the automatic extraction of sync edges in all streams
-save=2,0,5,20:60        ;save subset of probe chans (js,ip1,ip2,chan-list)
-pass1_force_ni_ob_bin   ;write pass one ni/ob binary tcat file even if not changed
-supercat={dir,run_ga}   ;concatenate existing output files across runs (see ReadMe)
-supercat_trim_edges     ;supercat after trimming each stream to matched sync edges
-supercat_skip_ni_ob_bin ;do not supercat ni/ob binary files
-dest=path               ;alternate path for output files (must exist)
-out_prb_fld             ;if using -dest, create output subfolder per probe
```


