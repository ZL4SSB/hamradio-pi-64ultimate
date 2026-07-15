# HRPU Logbook

The local logbook stores UTC, callsign, grid, frequency, band, mode, sent and
received reports, and notes in SQLite. Frequency, band and mode come from shared
Radio State. Confirm them before saving. Callsign is required.

**Export ADIF** writes all records in chronological order. Keep backups of both
the SQLite database and ADIF exports. LoTW, QRZ, ClubLog and eQSL are future
adapters; HRPU does not store or ship credentials for them.
