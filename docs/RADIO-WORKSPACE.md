# Radio Workspace and CAT Broker

Radio is the operator view of the shared Station Core. Enter frequency in MHz,
select mode, VFO and split, and use PTT only after a radio profile is configured.
The header reflects the same state used by Digital, Logbook and Satellites.

HRPU must own the physical CAT port. **Probe CAT Backend** checks for supported
Hamlib utilities; detection is not a radio connection. Broker clients use the
configured TCP endpoint. Reconnect counters and polling state are diagnostic.
Never let two programs open the same serial device directly.
