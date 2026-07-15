# HRPU R7 Unified Core

R7 introduces a shared station state. The purpose is to stop every workspace
from opening the physical radio, audio interface, rotator or station data
independently.

## Shared radio state

- radio identity
- frequency
- band
- mode
- RX/TX
- VFO
- split
- RIT/XIT state boundary
- CAT status
- audio routing profile
- rotator heading

Radio, Digital, Radio Map, Logbook, Satellite/Rotator and future GPIO services
all consume the same state.

## CAT broker boundary

HRPU owns the physical radio connection. External applications are intended to
use documented HRPU broker interfaces rather than competing for the same serial
port. R7 detects Hamlib utilities and exposes the broker/client state in the UI.

## Digital workspace

The R7 Digital page is an operating workspace and shared-state integration
boundary. It is not represented as a live FT8/FT4 decoder yet. Preview decode
activity is labelled clearly and feeds the Radio Map using the same spot model
that future independent HRPU decoders/adapters will use.

## Logbook

R7 adds an HRPU-owned SQLite logbook and ADIF export. A QSO is logged using the
current shared frequency/band and current digital operating mode.

## Satellites and rotator

R7 adds a shared satellite/rotator state boundary and azimuth/elevation display.
The included targets are preview geometry only. Live TLE ingestion, Doppler and
rotator protocol adapters are separate implementation stages.

## Source provenance

No Decodium, Nexus or WSJT-X source code is included. R7 is an independent HRPU
implementation based on HRPU requirements and general amateur-radio workflows.
