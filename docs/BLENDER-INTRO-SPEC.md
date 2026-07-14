# HRPU Blender Intro Specification

## Duration

5 seconds.

## Scene

### 0.0–1.5 seconds

- photorealistic Earth in space
- cloud layer and atmospheric rim
- visible day/night terminator
- gentle camera approach

### 1.5–3.2 seconds

- realistic controller board or Raspberry Pi enters orbit
- subtle board rotation
- power/activity LED pulse
- radio propagation arcs illuminate around Earth

### 3.2–4.4 seconds

- tower and station marker near New Zealand
- several radio paths animate toward other continents
- camera settles into final composition

### 4.4–5.0 seconds

- title fades in:
  `HAMRADIO-PI ULTIMATE`
- fade to dark lower third for HRPU's live loading overlay

## Important

Do not render loading text, version numbers, buttons or progress bars into the
video. HRPU draws those live over the video so version and startup status remain
accurate.

## Earth imagery

Use imagery with clear redistribution rights, such as NASA public imagery,
subject to its attribution and usage conditions. Do not use Google Earth
imagery.

## Output names

- `assets/video/hrpu-intro-720p.webm`
- `assets/video/hrpu-intro-1080p.webm`
