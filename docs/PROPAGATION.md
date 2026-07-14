# Native HRPU Propagation

HRPU includes its own propagation backend and frontend.

## Internal address

```text
http://127.0.0.1:8765
```

The page is embedded in the main HRPU window through Qt WebEngine.

## Station profile

The propagation module automatically reads the callsign and Maidenhead locator
stored in the HRPU station profile. The operator does not enter those details
twice.

## DX cluster

Configure the optional DX-cluster connection under **Preferences → Live
Propagation / DX Cluster**:

- host
- port
- login callsign
- enable live connection
- demo mode

When a login is blank, HRPU uses the station-profile callsign.

## Demo mode

Demo paths are retained when no live cluster is configured or no current live
spots are available.

## Service control

Use either the Propagation page or **Station Tools → Propagation**:

- Start
- Stop
- Restart
- Refresh Status

## Raspberry Pi

The installer creates and enables the user systemd service:

```text
~/.config/systemd/user/hrpu-propagation.service
```

## Windows

HRPU starts the local server automatically and stops its child process when the
application exits.
