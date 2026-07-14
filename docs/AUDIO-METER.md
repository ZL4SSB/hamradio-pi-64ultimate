# Live Audio Meter and Spectrum

Open **System Tools → Audio Test** and select **Start Monitor**.

The monitor displays:

- current RMS level
- peak level
- clipping warning
- spectrum from 0 to 6 kHz
- dominant frequency
- estimated occupied bandwidth

The occupied bandwidth is estimated from FFT bins above 10% of the current
spectral peak. It is intended as a setup aid rather than laboratory-grade
measurement.

Audio is analysed in memory and is not saved or transmitted.


## Peak Hold

Enable **Peak Hold** to draw a bright marker above each spectrum bar.

- Fast: markers fall quickly
- Medium: recommended for voice
- Slow: longer visual hold

Use **Clear Peaks** to reset all markers immediately.
