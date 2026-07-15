# Changelog

## 4.6 Rebuilt R7 — Unified Core

- Carried the full R6 Radio Map and propagation work forward.
- Added one shared HRPU Radio State.
- Added Radio workspace and shared frequency/band/mode/PTT/split context.
- Added an HRPU CAT Broker boundary with Hamlib utility detection.
- Added external CAT client registration state.
- Added a Digital operating workspace connected to shared radio and Radio Map state.
- Added clearly labelled preview decode activity for UI/integration testing.
- Added HRPU-owned SQLite Logbook.
- Added ADIF export.
- Added Satellites & Rotator workspace and shared AZ/EL state boundary.
- Added Radio Audio Profile under System Tools.
- Added source-provenance documentation for the unified core.
- No Decodium, Nexus or WSJT-X source was merged.


## 4.6 Rebuilt R6 — Radio Map

- Expanded the Propagation greyline prototype into a full Radio Map workspace.
- Added clickable target bearing, long-path bearing and distance.
- Added target sunrise, sunset and greyline-window calculations.
- Added station marker from the saved Maidenhead locator.
- Added DX, decoded, WSPR, beacon, grid, sun and path overlay controls.
- Added NCDXF/IARU beacon schedule presentation.
- Added VHF propagation awareness.
- Added major meteor-shower awareness and ZHR display.
- Added HRPU propagation-confidence framework.
- Added explicit proprietary-core dependency and provenance policy.
- No Decodium or WSJT-X GPL source was merged.


## 4.6 Rebuilt R5 — Full replacement

- Carries forward the fixed PyQt6 R4 baseline.
- Carries forward consolidated System Tools.
- Carries forward Applications installed checking and Remove controls.
- Removed Solar Wind and Interplanetary Bz cards from Propagation.
- Added a live key-free local greyline map under Estimated HF Band Conditions.
- Greyline calculation uses UTC solar position and twilight shading.
- Added station marker from the saved Maidenhead locator.
- Renamed Radio Dashboards to ROIP Dashboards (Radio over IP).
- No external map provider or map API key is required.


## 4.6 Rebuilt R4 FIXED

- Fixed R4 startup failure caused by the incompatible PySide6 backend.
- Rebuilt on the known-working PyQt6 4.6.4 baseline.
- Consolidated Hardware Manager, Station Profile and Preferences under System Tools.
- Removed Dashboard station-profile editing.
- Added Applications installed-state refresh.
- Added Remove buttons for installed applications.
- Linux removal uses apt with sudo confirmation.
- Windows removal uses the registered application uninstaller.
# 4.7.0 Station Core

- Added observable, authoritative radio state with VFO and RIT/XIT mutations.
- Added explicit CAT polling/reconnect diagnostics and disconnect lifecycle.
- Fixed SQLite connection locking on Windows and retained ADIF export.
- Added strict Maidenhead and great-circle path calculations.
- Added propagation model/evidence, beacon schedule, generic provider, and HRPU
  hardware-board boundaries that report unavailable data rather than inventing it.
- Added a standard-library regression suite for state, bands, locator/path maths,
  CAT state, beacon timing, SQLite, ADIF, and missing propagation adapters.
- Added Station Core architecture and full dependency/provenance register.
# 4.7.1 Functional Completion

- Connected Applications Install to a validated Raspberry Pi apt workflow.
- Added Help controls and individual guides for every managed application.
- Made WPSD and About cards actionable; unavailable privileged WPSD operations
  now open their safety guide instead of presenting decorative controls.
- Wired Digital TUNE to a safe unavailable-provider response and prevented preview
  satellite geometry from being marked as active tracking.
- Added UI/backend contract and application-help coverage tests.
