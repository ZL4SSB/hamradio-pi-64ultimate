# HRPU Ultimate Live Propagation

Self-hosted propagation module for HamRadio-Pi Ultimate. It does not use LU9DA images, remote map tiles, JavaScript CDNs, Flask, or Node.js. Runtime requires only Python 3 and a browser.

## Run

```bash
cd hrpu-propagation-module
python3 server.py
```

Open `http://127.0.0.1:8765`.

## Configure

Edit `config.json`. All user-specific station fields start blank. Enter a Maidenhead locator or latitude/longitude. Live cluster mode is disabled until a cluster host and login callsign are entered. Demonstration paths appear when no real spots exist.

## Feed a spot from HRPU

```bash
curl -X POST http://127.0.0.1:8765/api/spots -H "Content-Type: application/json" -d '{"reporter":"ZL4SSB","dx":"JA1ABC","frequency_khz":14074,"comment":"FT8"}'
```

The POST endpoint accepts one object or an array. The page reads `/api/propagation` and refreshes every minute.

## Integration

Run `server.py` as a local service and open the page in HRPU, or merge the two API handlers and static files into HRPU's existing Python web server. The important paths are `/api/propagation`, `/api/spots`, `/static/propagation.js`, `/static/propagation.css`, and `/static/data/world.geojson`.

DX-cluster spots normally contain callsigns rather than exact coordinates, so plotted positions use editable prefix centroids in `data/prefixes.json`. This is an activity overview, not exact station tracking.
