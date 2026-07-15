# HRPU Dependency and Source Provenance Policy

HRPU is being designed to remain capable of proprietary / closed-source commercial release.

| Licence family | HRPU policy |
| --- | --- |
| MIT / BSD / ISC | Accept with notices |
| Apache-2.0 | Accept with notices and review |
| LGPL | Review linkage and distribution obligations |
| GPL | Do not merge into the proprietary HRPU executable |
| AGPL | Do not use in the proprietary HRPU core |
| Unknown | Do not use until provenance is resolved |

## Dependency register

| Name | Version | Purpose | Licence | Source | Integration | Commercial review |
| --- | --- | --- | --- | --- | --- | --- |
| Python | 3.11+ | Application runtime and standard-library services | PSF-2.0 | python.org | Runtime | Accepted; preserve notices |
| PyQt6 | 6.x | Desktop UI and QML bridge | GPL-3.0/commercial dual licence | riverbankcomputing.com | Linked | Commercial PyQt licence required for proprietary distribution |
| Qt 6 | 6.x | QML/Quick UI runtime | LGPL-3.0/commercial dual licence | qt.io | Dynamically linked | Distribution/linkage review required |
| SQLite | Runtime bundled | Local HRPU logbook | Public domain | sqlite.org | Python standard-library module | Accepted |
| Hamlib utilities | User/system supplied | Optional CAT process/TCP provider | LGPL-2.1+ | hamlib.github.io | Separate process | Review packaging; no Hamlib code merged |

No new third-party package was added in 4.7. The test suite uses only Python's
standard library.

## R6 provenance note

The R6 Radio Map, greyline, target calculations, beacon schedule presentation,
meteor awareness and propagation-confidence framework are independent HRPU
implementations. No Decodium or WSJT-X source code is included.

Decodium and other GPL applications may be supported later as separate external
applications through documented interoperability interfaces after licence review.


## R7 unified-core provenance

`src/core_services.py`, the Radio, Digital, Logbook and Satellites/Rotator
workspaces, CAT broker boundary and radio-audio profile model are new HRPU code.
They do not contain copied Decodium, Nexus or WSJT-X source.
