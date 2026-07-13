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
