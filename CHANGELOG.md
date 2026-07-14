# Changelog

## 1.2.0

### Cinematic startup

- Added video-ready splash playback with Qt Multimedia.
- Added automatic 720p and 1080p intro selection.
- Added real loading stages and percentage progress.
- Added a two-second Skip control.
- Added immediate animated fallback when video is missing or unsupported.
- Added Blender intro specification and render placement instructions.


## 1.1.0

### Native propagation

- Integrated `hrpu-propagation-module` as a core HRPU component.
- Removed the external W5MMW/LU9DA propagation page and image dependency.
- Added local stdlib-only server at `http://127.0.0.1:8765`.
- Added bundled GeoJSON coastline and callsign-prefix data.
- Added embedded Qt WebEngine frontend.
- Added automatic Station Profile callsign and locator synchronisation.
- Added DX-cluster preferences and retained demo mode.
- Added Running, Stopped, Connection Error and Last Update reporting.
- Added Start, Stop, Restart and Refresh controls.
- Added Raspberry Pi user-systemd service.
- Added Windows automatic process management.
- Added updater preservation and clean uninstall handling.


## 1.0.0

First completed public release.

### Interface

- Final Dashboard, Applications, Radio Dashboards, WPSD Centre, Propagation,
  Shack Clock, Station Tools, Preferences, Help and About pages
- Removed Station Profile from the sidebar; profile editing remains available
  from the Dashboard
- Added five selectable dark themes
- Added responsive About layout
- Fixed Help navigation
- Fixed Dashboard activity-log button

### Propagation

- Replaced NOAA-derived HRPU cards with the live W5MMW propagation website
- Added Back, Forward, Refresh, Home and Open in Browser controls
- Removed NOAA background polling and its failed-feed errors

### WPSD

- Added official project, download, manual and Raspberry Pi Imager actions
- Added direct `wpsd.local` dashboard action
- Added access to configured Radio Dashboards

### Station Tools

- Hardware and USB scanning
- Driver overview
- Microphone and speaker tests
- Live audio meter, spectrum and Peak Hold
- Time synchronisation and GPS/PPS status
- Cloudflare/Google network testing
- Storage checks
- Program and dependency updates
- Diagnostics and support bundle
- Settings backup

### Installers

- Windows Desktop and Start Menu shortcuts
- Raspberry Pi Desktop and Ham Radio menu entries
- Optional launch after installation
- Optional start at login
- Public anonymous Raspberry Pi installer

### Privacy

Fresh installations contain no callsign, locator, DMR ID, email address,
password, API key or private URL.
