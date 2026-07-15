# HRPU Station Core Architecture

Version 4.7 establishes a single authoritative station domain. UI workspaces
request changes through services and consume immutable snapshots; they must not
open serial, audio, GPIO, network-provider, rotator, or TLE resources directly.

## Boundaries

```text
QML workspaces -> PyQt6 adapter -> Station services -> Provider interfaces
                                      |                    |
                                      |                    +-- Hamlib process/TCP
                                      |                    +-- audio provider
                                      |                    +-- map/data adapters
                                      |                    +-- board/MCU provider
                                      +-- SQLite logbook
```

`RadioStateService` owns radio identity, frequency/band/mode, PTT, VFO, split,
RIT/XIT, power, CAT, audio routing and rotator state. Subscribers receive a new
snapshot after each accepted mutation.

`CatBroker` is the sole physical-CAT ownership boundary. Hamlib may be used only
through its documented executable/TCP interfaces after distribution review.
Detection of Hamlib does not imply a connected radio.

`PropagationEngine` separates model prediction from observed evidence. Missing
WSPR, PSK Reporter, DX Cluster, beacon, ionospheric, or model adapters return
`unavailable` and `None`; the engine never fabricates live values.

`HardwareBoardService` exposes capabilities through a provider and defaults to
an unarmed unavailable provider. Raspberry Pi GPIO is not referenced by UI code.

Digital decoding, satellite TLE geometry, Doppler correction, external logbook
uploads, MapLibre/MapTiler, and MCU board control remain provider boundaries.
Any demonstration data must carry a PREVIEW or DEMO label.

## Platforms

Raspberry Pi OS Trixie is primary, Windows is supported, Android is a future
target, and iOS is outside scope. Platform-specific operations remain behind
providers. No API keys or user credentials are stored in source.
