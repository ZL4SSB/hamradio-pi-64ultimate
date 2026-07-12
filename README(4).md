# HamRadio-Pi Ultimate v0.3.5

This update connects saved weather settings to the main dashboard.

## Added

- Live weather on the dashboard.
- Automatic refresh using the saved interval.
- Manual **Refresh Weather** button.
- Open-Meteo current conditions.
- OpenWeather current conditions.
- Weather loading in a background thread so the window stays responsive.
- Friendly messages when weather is not configured or cannot be reached.

## Install

Replace or add:

```text
src/dashboard.py
src/services/weather_service.py
config/version.json
```

## Test

Run:

```powershell
python src/app.py
```

Then:

1. Open **Settings → Data Sources**.
2. Configure and test weather.
3. Click **Save Settings**.
4. The dashboard should immediately update the Weather row.
5. Click **Refresh Weather** to test manual refreshing.

## Commit

```powershell
git add src/dashboard.py src/services/weather_service.py config/version.json
```

```powershell
git commit -m "Display live weather on dashboard"
```

```powershell
git push
```
