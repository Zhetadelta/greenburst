* peak_find.py      : Finds RFI in bandpass
* pointing_dump.py  : Dumps telescope positions in json format from redis database
* plot_cand.py      : Plots the heimdall candiates along with RFI masks
* pointing_test.py  : Dumps all redis keys possible
* Stage_1.py        : Stage 1: Get RFI Flags, run heimdall


# Basic usage
Running `circusd --daemon --pidfile pp circus.ini` will start up the GPU queue server `gpu_server.py`, the UDP socket to monitor incoming data `udp2fil`, `pointing_dump.py`, and stages 1-3 as circus-managed processes. The circusd process ID will be saved in `pp`. 

Process monitoring is done with `circus-top`.

To stop all processes, run `circusctl quit`.

Logs are output to `/ldata/dev_tests/circus_tests/`.

## Manual processing
All three stages can be run with specific files (as opposed to running on a queue). Stages 1 and 2 require `gpu_server.py` to be running as well. If the next stage is running as a daemon, the output of a previous stage can be automatically sent to it to reduce the amount of commands needed to fully reprocess archival data.

**All stages support `-h` for help, `-v` for verbose mode, and `-d` to run once as opposed to as a daemon.**

### Stage 1
Arguments:
  - `-m, --skipmetadata`    
    - Skip metadata indexing from serendip6. **Note:** this will result in pointing data not being recorded, and should only be used for offline testing.
  - `-n {NCHANS}, --nchans {NCHANS}`
    - Number of chans to calculate median over for RFI filtering. (default: 64) **Currently unused.**
  - `-s {SIGMA}, --sigma {SIGMA}`
    - Sigma over which values are tagged as RFI (default: 5). **Currently unused.**
  - `-r, --return`
    - Log filename instead of adding to stage 2 queue. Use for testing or manual processing.
  - `-f {FILENAME}, --file {FILENAME}`
    - Filterbank file to process. Only functions alongside the `-d` flag.

### Stage 2
Arguments:
  - The following arguments set filters for candidates output by `heimdall` in stage 1:
    - `-s {SNR}, --snr {SNR}`     
      - Minimum SNR (default: 8.0)
    - `-w {WIDTH}, --width {WIDTH}`
      - Maximum width (in samples) (default: 7)
    - `-D DM, --dm DM`        
      - Minimum DM (default: 20)
    - `-m MEMBERS, --members MEMBERS`
      - Minimum number of members in cluster (default: 5)
  - `-o, --outfile`
    - Write output to file instead of adding to stage 3 queue. Use for testing or manual processing.
  - `-f {FILES}, --files {FILES}`
    - Glob that matches candidate files. Usually will end with `/*cand` to match all output candidates. Only functions alongside the `-d` flag.

### Stage 3
Arguments:
  - `-f FILE [FILE ...], --file FILE [FILE ...]`
    - .h5 file (or sequence of files) to process.
  - `-F {FILELIST}, --filelist {FILELIST}`
    - Output file from stage 2 containing list of valid outputs.
