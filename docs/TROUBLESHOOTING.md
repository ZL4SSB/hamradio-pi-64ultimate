# Troubleshooting

## Application does not start

Run the application from a terminal and inspect:

```text
reports/qml-startup-error.log
```

## No microphone or speakers

Open **System Tools**, select **Detect Devices**, then test the speaker and
microphone separately.

## Radio Dashboard does not load

Confirm the same URL opens in a normal browser and that the dashboard and
computer are on the same network.

## Propagation data unavailable

Run **System Tools → Network Test**. NOAA data requires working internet and DNS.

## Installation problem

Review:

```text
reports/install.log
```

Create a support bundle from **Help → Create Support Bundle**.
