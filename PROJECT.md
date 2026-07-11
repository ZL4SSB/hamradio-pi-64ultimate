# HamRadio-Pi Ultimate

## Mission

HamRadio-Pi Ultimate aims to be the easiest way to transform a standard Raspberry Pi OS installation into a complete amateur radio workstation.

**No Linux knowledge required.**

**One command. One wizard. One Ham Radio menu.**

## Main Goal

A user should be able to:

1. Install Raspberry Pi OS 64-bit.
2. Run one installer command.
3. Choose the type of amateur radio station they want.
4. Allow the installer to check compatibility and available storage.
5. Reboot into a ready-to-use amateur radio environment.
6. Find all installed radio applications under one dedicated **Ham Radio** menu.

## Supported Platform

Version 1.0 will target:

* Raspberry Pi OS Desktop 64-bit
* Debian Trixie as the preferred base
* Debian Bookworm where practical
* Raspberry Pi 4
* Raspberry Pi 400
* Raspberry Pi 5
* Raspberry Pi 3 with a reduced software selection

Version 1.0 will focus only on the standard Raspberry Pi desktop environment.

## Design Rules

1. Never require Linux knowledge from the user.
2. Never ask technical Linux questions when plain English can be used.
3. Detect hardware and software wherever practical.
4. Explain errors clearly and provide a suggested solution.
5. Check available disk space before installation.
6. Never begin an installation that is likely to fill the storage device.
7. Allow the installer to be safely run again.
8. Keep installation code modular and maintainable.
9. Place all installed amateur radio applications under one dedicated **Ham Radio** menu.
10. Do not modify original application launchers unnecessarily.
11. Keep essential station features free.
12. Supporter features must be optional convenience features only.

## Station Builder

Users choose the kind of station they want to build rather than selecting Linux package names.

Planned station profiles:

* Recommended Ham Station
* Digital Modes Station
* SDR Receiver Station
* APRS and Packet Station
* Satellite Station
* Contest Station
* Emergency Communications Station
* Headless Radio Server
* Complete Collection
* Custom Installation

Each station profile will define:

* Software groups
* Estimated storage requirement
* Desktop or headless operation
* Recommended hardware support
* Menu categories

## Storage Handling

Before installing software, the installer must calculate:

* Available storage
* Estimated installation size
* Required safety reserve
* Estimated space remaining afterward

If there is not enough space, the installer must offer smaller alternatives such as:

* Digital Modes only
* SDR only
* APRS and Packet only
* Satellite tools only
* Radio Programming only
* Headless Server only
* Custom selection

The installer must not continue if doing so would leave dangerously low free space.

## Installation Modes

### Recommended Ham Station

A balanced selection of commonly useful amateur radio applications.

### Complete Collection

Every supported application and software group.

### Custom Installation

The user selects individual station groups or programs.

### Headless Radio Server

Server applications without a local graphical desktop requirement.

## Desktop Menu

The installer will create one main menu category:

**Ham Radio**

Planned subcategories:

* Digital Modes
* SDR
* APRS and Packet
* Satellite
* Logging and Contesting
* Radio Programming
* Test Equipment
* Server Tools
* Utilities
* Ham Shack Control Centre

Programs installed by HamRadio-Pi Ultimate should not remain scattered throughout unrelated desktop menu sections where this can safely be avoided.

## First Run Wizard

After installation and reboot, a guided setup wizard will help configure:

* Callsign
* Maidenhead locator
* Radio manufacturer and model
* Hamlib radio selection
* CAT serial port
* Audio input
* Audio output
* Connected SDR hardware
* Optional startup services

The wizard should use plain language and avoid Linux terminology.

## Ham Shack Dashboard

A graphical dashboard will provide:

* Station status
* Connected hardware
* Application launchers
* Updates
* Repair tools
* Backup and restore
* Documentation
* Settings
* Support information

The dashboard will use large tiles and clear status indicators.

## Community Edition

The Community Edition will always include everything required to install, operate, update, and repair a complete amateur radio station.

Essential features will not be locked behind payment.

## Supporter's Edition

Users who donate at least $5 USD may receive an activation code by email.

Possible supporter features:

* Additional dashboard themes
* Automatic backup scheduling
* Extended station health information
* Detailed hardware information
* Update notifications
* Early access to new optional features

Supporter features must remain convenience features and must not prevent Community Edition users from operating or repairing their station.

## Project Structure

```text
hamradio-pi-64ultimate/
├── install.sh
├── README.md
├── PROJECT.md
├── config/
├── docs/
├── icons/
├── logs/
└── scripts/
```

## Version 1.0 Priorities

* System compatibility checks
* Internet check
* Storage check
* Station Builder
* Software group database
* Group installation engine
* Recommended installation
* Complete installation
* Custom installation
* Dedicated Ham Radio menu
* Logging
* Clear error messages
* First Run Wizard
* Basic Ham Shack Dashboard
* Update and repair functions

## Future Ideas

Future versions may include:

* Fully graphical installer
* Offline installation media
* Automatic hardware detection
* Portable club installer
* Remote station management
* Plugin system
* Prebuilt Raspberry Pi image

## Project Motto

**Build your station, not your software list.**

## Completion Message

The finished installer should end with:

> 73!
>
> Your Raspberry Pi amateur radio station is ready.
>
> Thank you for using HamRadio-Pi Ultimate.
>
> 73 de ZL4SSB
