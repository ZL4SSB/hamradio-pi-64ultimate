# HamRadio-Pi Ultimate 4.4.0

One-click Raspberry Pi test release.

## Easiest public installation

The repository must be public. No GitHub account or login is required.

Copy and paste this single command into a Raspberry Pi terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/zl4ssb/hamradio-pi-64ultimate/main/install-public.sh | bash
```

The installer automatically:

- downloads HamRadio-Pi Ultimate
- detects the Raspberry Pi OS environment
- installs only packages available for that OS
- handles Debian package-name changes
- installs PyQt6 and Qt Quick/QML
- creates the desktop launcher and icon
- runs a self-test
- starts the program when a graphical desktop is active

## Installing an extracted ZIP

Open a terminal inside the extracted folder and run:

```bash
chmod +x install.sh
./install.sh
```

## Starting later

From the desktop menu, select **HamRadio-Pi Ultimate**, or run:

```bash
hamradio-pi-ultimate
```

## Updating later

```bash
cd ~/hamradio-pi-64ultimate
./scripts/update-public.sh
```


## ROIP Dashboards

Embedded EuroNode/MMDVM/Pi-Star/WPSD dashboard viewer with saved URLs, navigation, testing, zoom and external-browser support.


## 4.4.2 visual fixes

- removed duplicate top-right window buttons
- moved and resized the dashboard logo
- increased spacing between CPU, load and disk widgets
- improved label and field contrast throughout Preferences
- made checkbox text clearly visible
- moved Station Profile inputs left
- improved Station Profile label, placeholder and typed-text readability


## 4.5.0 — Operational Propagation page

The Propagation menu is now functional and downloads live data from the NOAA
Space Weather Prediction Center.

Displayed values:

- 10.7 cm solar radio flux
- Planetary Kp index
- Solar-wind speed and density
- Interplanetary magnetic-field Bz
- GOES X-ray class
- Geomagnetic activity description
- Estimated conditions for 160–10 metres

Data refreshes every five minutes and can also be refreshed manually.


## 4.5.1

- Replaced fragile NOAA propagation URLs with current operational feeds
- Each propagation reading now fails independently
- A missing NOAA value no longer breaks the whole page
- Preferences now persist hardware defaults, update channel and backup choice
- Startup hardware scan and update checks use the saved Preferences options
- HamClock, splash, theme and startup choices save and reload


## 4.6.0 — Operational System Tools

System Tools now provides:

- microphone and speaker detection on Raspberry Pi and Windows
- speaker test tone
- three-second microphone level test
- internet and DNS test
- disk-space and write-access test
- USB-device test
- diagnostics report
- terminal launcher
- program update button
- dependency update button

The splash screen remains visible for five seconds. Donate controls are now
prominent on both the splash screen and sidebar.

The dashboard wordmark was rebuilt with a transparent background and moved
further upward and to the right.


## 4.6.1 — Preferences and Help

- completed Preferences settings centre
- added settings export, reset and settings-folder controls
- added searchable in-app Help
- added full installation and troubleshooting guides
- added support-bundle creation
- added direct access to project and issue pages
- fixed public ZIP installer folder detection after repository rename


## 4.6.2 — Live audio meter and spectrum

System Tools now includes a live microphone monitor with:

- real-time RMS audio level
- peak level
- clipping warning
- 0–6 kHz spectrum
- dominant frequency
- estimated occupied bandwidth
- Start/Stop monitoring

Audio is analysed in memory only. It is not saved or transmitted.


## 4.6.3 — Spectrum, navigation and preferences

- upgraded the live spectrum appearance with grid lines and clearer labels
- added optional per-bar Peak Hold markers
- added Fast, Medium and Slow peak decay
- added Clear Peaks
- added spectrum defaults to Preferences
- changed Network Test to Cloudflare with Google fallback
- removed the redundant Updates sidebar page
- kept all program and dependency updates under System Tools
- enlarged and darkened Radio Dashboard back, forward and refresh controls


## 4.6.4

- Fixed missing shared QML component import in System Tools.
- Restored DarkComboBox and DarkCheckBox availability.
- Checked all QML pages that use shared controls.


## 4.6 Rebuilt R4 FIXED

Rebuilt from the known-working PyQt6 4.6.4 baseline.

Hardware Manager, Station Profile and Preferences are accessible only through
System Tools. Dashboard station details are display-only.

Applications now performs installed-state checks and shows Remove for installed
programs. Linux removal uses apt with sudo confirmation. Windows uses the
registered uninstaller.


## 4.6 Rebuilt R5 — Full replacement build

This is a full replacement build based on the fixed PyQt6 R4 baseline and
carries the existing System Tools consolidation and Applications manager
forward.

### Propagation
- Removed the Solar Wind card.
- Removed the Interplanetary Bz card.
- Added a live local greyline world map directly below Estimated HF Band Conditions.
- The map calculates the solar position and day/night twilight from UTC.
- The saved HRPU Maidenhead locator is used for the station marker.
- No Google Maps, Snazzy Maps, Mapbox, Esri tiles, external map tiles or API key are required.

### ROIP
- Renamed the visible Radio Dashboards menu/page wording to ROIP Dashboards.
- ROIP is identified as Radio over IP.


## 4.6 Rebuilt R6 — Radio Map and propagation awareness

R6 keeps the fixed proprietary-capable HRPU codebase and does not merge GPL
Decodium or WSJT-X source.

New Propagation functions:
- Large DXChrono-inspired but independently implemented Radio Map / greyline workspace.
- Click target for bearing, long-path bearing, distance, sunrise, sunset and greyline window.
- Station marker from the saved Maidenhead locator.
- Overlay controls for DX, decoded activity, WSPR, beacons, grid, sun and paths.
- Demo spot lifecycle/framework ready for documented live data adapters.
- NCDXF/IARU beacon schedule panel.
- VHF propagation awareness cards.
- Major meteor-shower awareness and ZHR display.
- HRPU propagation-confidence framework ready to combine live observed WSPR,
  PSK Reporter and DX Cluster activity with the solar model.

No Decodium source was copied or merged.


## 4.6 Rebuilt R7 — Unified Core

R7 carries the complete R6 baseline forward and adds a new shared station-core
architecture.

New first-class workspaces:

- Radio
- Digital
- Logbook
- Satellites & Rotator

New shared services:

- HRPU Radio State
- CAT Broker boundary with Hamlib detection
- Radio audio-routing profiles
- Digital workspace state and map-feed model
- SQLite QSO logbook
- ADIF export
- Satellite/rotator state boundary

The R7 Digital and satellite pages clearly label preview data. They are not
presented as completed live RF decoders or live TLE tracking.

See `docs/UNIFIED-CORE.md`.
# HamRadio-Pi Ultimate 4.7.1 Functional Completion

The 4.7.1 replacement build preserves the 4.6/R7 workspaces and introduces tested,
platform-neutral station services. See `docs/STATION-CORE-ARCHITECTURE.md` for the
ownership rules and provider boundaries. Features without configured adapters
remain explicitly marked PREVIEW, DEMO, or unavailable.

Application cards now install (Raspberry Pi), launch, remove and open dedicated
help. WPSD operations that require a future privileged media provider open a
safety guide and report unavailable; they never claim a destructive operation
succeeded. Digital decoding/modulation and live satellite tracking likewise
remain clearly labelled provider boundaries.
