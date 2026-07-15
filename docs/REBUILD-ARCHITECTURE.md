# HRPU 4.6 Rebuilt Architecture

This is the new baseline for HamRadio-Pi Ultimate.

## Product rules

1. Stable before flashy.
2. One function has one obvious home.
3. No duplicate Station Profile or Update pages.
4. Cross-platform first: Raspberry Pi OS and Windows.
5. Hardware authority stays in Python/native services.
6. Rich visual modules may use local HTML/JavaScript.
7. Browser code never directly keys a transmitter or drives GPIO.
8. Fresh installs ship with blank station identity, email and password fields.
9. Local/offline services are preferred where practical.
10. A page is not called complete until its controls perform real actions.

## Application layers

### Operator shell
QML/Qt Quick owns navigation, page layout, keyboard/mouse interaction,
theme presentation and embedded local web views.

### Core services
Python owns settings, hardware discovery, audio capture, CAT, GPIO, PTT,
rotator interfaces, driver inspection, updates and OS integration.

### Local visual modules
HTML/CSS/JavaScript is suitable for propagation, Shack Clock, spectrum,
waterfall, maps, station-history charts and high-rate dashboards.

### Future station bus
Hardware services expose typed station state to the UI. Radio, rotator,
amplifier, antenna, GPS and audio state should not be read independently by
every page.

## Operator workspaces

- Dashboard
- Applications
- WPSD Centre
- Propagation
- Radio Dashboards
- Shack Clock
- System Tools
- Preferences
- Help
- About

Station Profile is data, not a duplicate navigation destination.
Updates belong in System Tools.
Hardware Manager belongs in System Tools.

## Design direction

Keep the 4.6 startup screen and dark-teal identity. Modernise spacing,
readability, responsive layout and operator workflow. Avoid dense legacy
toolbars and tiny controls associated with older amateur-radio desktop software.


## Single-owner UI rule

Every configurable function has exactly one editing location.

- Station identity → System Tools → Station Profile
- Hardware discovery → System Tools → Hardware Manager
- Appearance → System Tools → Appearance
- Startup behaviour → System Tools → Startup
- Maintenance → System Tools → Maintenance

Dashboard cards display shared state only. They do not duplicate configuration.
