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


## Radio Dashboards

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


## 4.7.0 — Ultimate Shack Clock

Added a native Shack Clock page with:

- local and UTC clocks
- station identity
- sunrise and sunset from Maidenhead locator
- daylight/night state
- simplified greyline display
- NOAA propagation readings
- estimated HF band conditions
- optional external clock fallback

The Dashboard HamClock button now opens the built-in Shack Clock.


## 4.8.0 beta — Animated startup test

This beta adds an original five-second animated startup sequence featuring:

- rotating stylised Earth
- orbiting generic Ultimate controller board
- amateur-radio tower
- animated RF wavefronts
- star field
- loading bar
- Donate button
- Skip button available after two seconds

The animation uses original QML artwork and does not copy a movie-studio logo
or use official Raspberry Pi board artwork.


## 4.8.1 beta — Desktop integration

Installers now provide:

### Windows

- optional Desktop shortcut
- optional Start Menu folder and shortcut
- HRPU multi-resolution `.ico`
- no-console launcher
- optional launch after installation
- optional start at login under Preferences

### Raspberry Pi

- optional Desktop shortcut
- Ham Radio application-menu category
- HRPU PNG icon
- `hamradio-pi-ultimate` launcher command
- optional launch after installation
- optional start at login under Preferences


# 4.9.0-pre1 — Final consolidation before v1.0

- final simplified sidebar
- Station Tools consolidation
- hardware and driver overview
- audio meter and spectrum
- network, storage, update and diagnostic tools
- NTP/GPS/PPS time status
- native Shack Clock
- fresh-install privacy
- polished About and Help
- Windows and Raspberry Pi shortcuts and installers


## 4.9.1-pre1 corrections

- removed propagation and HF condition cards from Shack Clock
- fixed Dashboard View Full Log
- removed Station Profile from sidebar
- replaced WPSD placeholder with working actions
- rebuilt Propagation in a clear solar-conditions layout inspired by W5MMW
- fixed Help navigation
- rebuilt About layout
- expanded Preferences to five visible theme choices


# Version 1.0.0

HamRadio-Pi Ultimate 1.0.0 is the first completed public release.

Highlights:

- final simplified menu
- live W5MMW propagation page
- native Shack Clock
- Radio Dashboards for EuroNode, WPSD and MMDVM
- operational WPSD Centre
- Applications manager
- Station Tools with hardware, drivers, audio, time, network, storage,
  updates, diagnostics and backups
- live microphone spectrum with Peak Hold
- selectable application themes
- Windows Desktop and Start Menu shortcuts
- Raspberry Pi Desktop and Ham Radio menu entries
- anonymous public installation without a GitHub account
- blank personal information on fresh installations


# Version 1.1.0 — Native propagation

- integrated the HRPU propagation module into the main project
- removed the W5MMW/LU9DA-style external propagation dependency
- bundled local coastline and callsign-prefix data
- added a stdlib-only local server on `127.0.0.1:8765`
- embedded propagation inside the HRPU window
- reused callsign and locator from Station Profile automatically
- added DX-cluster host, port, login, enable and demo-mode Preferences
- added Running, Stopped, Connection Error and Last Update states
- added Start, Stop, Restart and Refresh controls
- added Raspberry Pi user-systemd automatic startup
- added Windows automatic child-process startup
- preserved user settings through public updates
- added clean service/launcher uninstall handling


# Version 1.2.0 — Cinematic startup system

- added WebM cinematic intro playback
- automatic 720p Raspberry Pi / 1080p Windows selection
- real startup stage and percentage display
- skip control after two seconds
- silent playback by default
- automatic animated fallback if video is missing or fails
- no black-screen wait for failed video
- Blender render specification and asset naming included
