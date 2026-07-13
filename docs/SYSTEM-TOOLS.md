# System Tools

## Audio

The Audio Test detects playback and recording devices.

- Raspberry Pi uses ALSA (`aplay` and `arecord`) with optional PortAudio.
- Windows uses PortAudio through `sounddevice`, with Windows audio-endpoint
  discovery as a fallback.

Speaker Test plays a two-second 700 Hz tone.

Microphone Test records three seconds and reports peak and average signal
levels.

## Other tests

- Network and DNS connectivity
- Disk free space and write access
- USB-device count
- Full diagnostics report
- Terminal launcher

## Updates

Update Program uses the public anonymous installer on Raspberry Pi. It does not
require a GitHub account.

Update Dependencies opens a visible terminal so package progress and any
administrator-password prompt can be read.
