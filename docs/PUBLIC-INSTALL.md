# Public installation without a GitHub account

The repository must be public.

```bash
sudo apt update
sudo apt install -y curl
curl -fsSL \
  https://raw.githubusercontent.com/zl4ssb/hamradio-pi-64ultimate/main/install-public.sh \
  -o /tmp/install-hamradio-pi.sh
chmod +x /tmp/install-hamradio-pi.sh
/tmp/install-hamradio-pi.sh
```

This downloads the public branch archive from `codeload.github.com`.
It never runs `git clone` and never asks for credentials.
