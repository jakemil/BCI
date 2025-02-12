This repo will serve to store all software needed for FFT and Nueromorphic computing to analyze SSVEP
1. Set up BrainFlow in python environment to read in channel data from cyton board: set gain to x8 because using ThinkPulse sensors
2. Calibration
    - Test individual electrodes with the following EMG tests:
        - on the pre-frontal channels (usually 1 and 2 if you followed the numbering of the video), make sure you can detect eye blinking clearly
        - for all the channels, make sure jaw clenching generates a high frequencies and significantly higher amplitude artefact 
        - Next test is Alpha detection when you close your eyes (better be 2 people, or record your session).
        - Test against GUI

3. Read in brain waves
    - data format specs https://docs.openbci.com/Cyton/CytonDataFormat/
    