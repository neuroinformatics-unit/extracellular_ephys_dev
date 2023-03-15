# [The SPIKEGLX manual](https://github.com/billkarsh/SpikeGLX/blob/master/Markdown/UserManual.md)
Also see additional docs at [NI Tab](https://billkarsh.github.io/SpikeGLX/Sgl_help/NITab_Help.html)
and at [NP UTILS](https://djoshea.github.io/neuropixel-utils/imec_dataset/)

## Setup (not important for me)

The manual contains formation on installation, the _Configs folder, and each probe's folder labelled by probe
serial number that contains calibration files. Details on connection to remote server on startup, setting up
data storage directory and multi-drive splitting for very long runs

The manual also provides infortmation about the internal data stream.

## Data format (important for me)

Neuropixels is [build in collaboration](https://www.imec-int.com/en/expertise/health-technologies/neural-probes)
 with the not-for-profit international digital technologies research organisation IMEC. They produce the so called
 'imec' probes. This is why the probes are referred to as imec in neuropixels literature.

 SPIKEGLX supported streams:
 - imec0 : 1st connected probe, oeprating over PXIe (Nataion Instruments [connection module](https://www.ni.com/en-gb/support/documentation/supplemental/12/how-to-connect-signals-to-the-pxi-pxie-2532b.html)) or USB
 - imec1 : 2nd probe (optional)
 - imec2 : 3rd probe (optional
 - imec3 : 4th probe (optional)

 up to 4 probes can be connected at once.

 Connection via OneBox is also provided, and `nidq` for non-neuronal signals. The Whisper system is a 32X multiplexer add-on that plugs into an NI device, giving you 256 input channels. Whisper requires S-series devices (61xx).

 IMPORTANT: imec probes (currently) read out 384 channels of neuronal data and have 8 bits of status data.
    "Bit #0 signals that custom user FPGA code running on the Enclustra has detected an interesting neural event (NOT YET IMPLEMENTED). Bit #6 is the sync waveform, the other bits are error flags. Each probe is its own stream."

#### Channel Naming and Ordering

Each imec stream acquires up to three distinct types of channels:

1) AP (action-potential) - 16 bit channels
2) LF (local field) - 16 bit low-frequency channels (1/12 sampling rate of AP channel)
3) SY (for sync) - 16 bit sync input channel (sync is bit #6 waveform (it is single 0 or 1 trigger))

The syncing works (see CatGT docs for more details) by providing a single step function {0, 1} with frequency 1 second.
This step waveform is used for time syncing by aligning different input streams (e.g. probes) to the leading edge.

Note that at a minimum, all probes read out 384 AP channels and a single SY channel. In some versions, the probes
read out a separate LF channel (and so have 384 x 2 + 1 channels). I guess because the LF channel is just
AP channel with 1/12 sampling rate, in previous versions these were combined. I wonder why they were separated.

IMPORTANT:  "Throughout the software the channels are maintained in acquisition order. That is, each acquired sample (or timepoint)
contains all 384 AP channels, followed by the 384 LF channels (if present), followed by the SY channel." This is important
for understanding the multiplexing correction that occurs in CatGT.

#### Channel Naming

The channels are named with zero based indices, as `<TYPE><GROUP_NUM>;<TOTAL_NUM>`. So the channel AP0;0
is the first AP channel and first channel overall. LF0;385 is the first LF channel and 386th overall.

Note the other channel names (OneBox: XA, XD) and NIDQ (MN (i.e. multiplexed neural signed 16-bit channels), MA)

#### Channel Saving

AP and LF channels are saved separately (LF channel are 1/12th samplign rate i.e. 30 kHz / 12 = 2.5 kHz. The sync
channel is duplicated in both files. e.g.

`filename.imec0.ap.bin` is the AP data from the first probe and would contain `AP0;0 ... AP383;383 | SY0;768`.

`filename.imec0.lf.bin` is the LF data from the first probe and would contain `LF0;384 ... LF383;767 | SY0;768`.

Note that OneBox channels are handled differently (see docs).

Note that NIDQ channels are handled differently (see docs).

#### Shank Map

IMPORTANT: The mapping from channel ID to physical position on the probe is critical. It is used for
spatial channel averaging, activity visualisation, motion correction (e.g. kilosort). This applies to imec and nidq
streams as nidq can also be used to record from probes.

A neuropixels probe contains MANY channels. e.g. NP2.0 4 shank version has 5120 recording sites. However,
we can only record 384 channels per probe. This means we need to map what recording sites we want to
use to the channel.


The shank map is automatically derived from the imro table for imec probes. imec shank maps are internal, they
are not edited or saved directory. IMPORTANT: these are generated automatically. The user does not need to worry
about this. The user just needs to define a channel map is not using the default (see below).

The shank map first row is the header, containing the nubmer of shanks (e.g. 1 or 4 shank probe),
number of columns per shank and number of rows per shank. Imaging spatially, the number of rows is
the channels as spread along the shank from top to bottom.

The mapping is such that after the header, each channel gets 1 row in the shank map. For each channel,
its shank, column and row is provided in the form of a boolean (0 or 1). The 4th column tells if the channel is
used or not.You can set channels to unused by setting to zero in SpikeGLX IM Setup tab (e.g. if it is bad channel,
or for reference channels)

So to confirm, the first row is the header and the remaining rows are spatial information with the
headings:

`SHANK INDEX,        COLUMN INDEX,             ROW INDEX,             IS_USED`
```
0, 1, 480  # HEADER: nShanks, nColsPerShank, nRowsPerShank
0     0     0     1                 # first shank, first shank column, first row, used
0     1     0     1                 # first shank, second shank column, first row, used
0     0     1     1                 # first shank, first shank column, second row, used
0     1     1     1                 # first shank, second shank column, second row, used
....                                # one entry per spiking acquisition channel
```

The shank map is a mapping from acquisition channel to phyiscal probe location. This means there
can be more potential probe recording sites (num shanks x num cols per shank x num rows per shank),
than channels. For NIDQ maps (this is important), the number o ftable entries must equal MN).

#### [IMRO Table](https://billkarsh.github.io/SpikeGLX/help/imroTables/)

IMRO stands for imec-read-out. The docs are kind of hard to follow, but seems as expected this
maps the input channel to the physical location on the probe, with reference to the shank ID,
bank ID, and electrode ID (range 0 to 1279 on each shank).

#### Channel Map

To me, the difference between the channel map and shank map is not clear. At a guess, the channel
map is just used for viewing channels in SpikeGLX. The shank-map is more useful, contaning
the real-world mapping of the recording sites. Anyway, the channel position is in the `.meta` file
which we can use in all practical instances.

[This docs also contains nice information on this](https://cellexplorer.org/tutorials/channel-maps-tutorial/)

[This is quite nice](https://probeinterface.readthedocs.io/en/main/overview.html)

Some questions I cannot find the answer to:

* Does the channel map effect the order that the channels are saved to file? (docs only say order of GUI)
Why would you want to do this? (presumably if you only want to save a subset of channels)


#### Output File Format

`.bin`: binary file with no header. 16-bit channel data is packed and ordered exactly as described above. A single
'timepoint' is a _whole_ number of 16-bit words. One 16-bit word per analog channel, then at the rear any saved digital lines
bundled in 16-bit words.

`.meta`: ini-file fomrat text file. There is a Metadata.html file that documents
this format.

#### Synchronisation

Each stream (i.e. imec probe, onebox, nidq) has
its own start time and sample rate.

Sample rate calibration is available in SpikeGLX. This is important, initial sample rates 
of imec probe are often 30,000.60 Hz (72ms per hour error from 30 kHz).

Start time estimate is good to approximately 10 ms.

SpikeGLX has a channel to run a squarewave pulser for syncing. This is 1 Hz square wave.
The mode that sets this also ensures start times agree to within 1 ms. CatGt is used to align these
square-wave pulses from the leading edge.

See the [CatGT docs](https://billkarsh.github.io/SpikeGLX/help/syncEdges/Sync_edges/) for details information on how these 
sync pulses are used for alignment.

#### Gates and Triggers 

See a discussion here for [some background](https://github.com/SpikeInterface/spikeinterface/issues/628#issuecomment-1130216875)

Gates and triggers define how output files are written in spike GLX. One of the functions of CatGT is to
concatenate spikeglx output files into single, contigious recordings (i.e. CatGT = Concatenate Gates Triggers).

Note the concatenation process is not trivial, and it cannot be assumed that when one sub-file ends another begins. 
Sometimes these overlap and CatGT does a lot of work under the hood to string these together properly.

Overall it's a pretty neat system that allows writing files under 
[certain conditions](https://github.com/billkarsh/SpikeGLX/blob/master/Markdown/TrigTab_Help.md).
For example, you can write to file based on times, in 5 minute blocks or events in the data (e.g. AP detection - start saving data)

The docs are clear on this, setting the gate writes a new folder where all subsequent
files from triggers on (start writing) and off (stop writing) go. The `t` idx on the filename
is incremented by 1 with each trigger. When the gate goes low, no file writing can take place.
Similar to trigger, the gate index `g` starts at 0 and ingrements as the gate
switches e.g. the gate goes high, then low, then high again, a new folder is opened and all
subsequent trigger switches are written to filename with `g1` index.





