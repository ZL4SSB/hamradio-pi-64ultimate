# Fresh Raspberry Pi OS Trixie Installation

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/zl4ssb/hamradio-pi-64ultimate.git
cd hamradio-pi-64ultimate
chmod +x install.sh scripts/*.sh src/app.py
./install.sh
```

The installer downloads all required dependencies and performs an off-screen
Qt/QML self-test.

Start afterward with:

```bash
~/.local/bin/hamradio-pi-ultimate
```
