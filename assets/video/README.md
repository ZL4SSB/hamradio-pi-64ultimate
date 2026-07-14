# HRPU Cinematic Intro Assets

The startup system automatically looks for:

- `hrpu-intro-720p.webm`
- `hrpu-intro-1080p.webm`

Place rendered Blender WebM files in this folder.

Selection:

- screens narrower than 1600 pixels: 720p
- screens 1600 pixels or wider: 1080p

Recommended exports:

## Raspberry Pi

- 1280 × 720
- 30 fps
- VP9 WebM
- 5 seconds
- no audio, or a separate optional audio track
- target bitrate 3–5 Mbps

## Windows

- 1920 × 1080
- 30 or 60 fps
- VP9 WebM
- 5 seconds
- target bitrate 6–10 Mbps

When either file is missing or cannot be decoded, HRPU immediately uses the
built-in animated fallback. The program does not wait for a broken video.
