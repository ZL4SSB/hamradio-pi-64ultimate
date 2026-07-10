#!/bin/bash

#################################################
# HamRadio-Pi-64-Ultimate
# Simple Ham Radio Installer
# Version 0.1
#################################################

VERSION="0.1"

LOGFILE="$HOME/hamradio-install.log"


echo "=================================" | tee -a $LOGFILE
echo " HamRadio-Pi-64-Ultimate" | tee -a $LOGFILE
echo " Version $VERSION" | tee -a $LOGFILE
echo "=================================" | tee -a $LOGFILE


# Check operating system

echo
echo "Checking system..."

source /etc/os-release

echo "OS:"
echo "$PRETTY_NAME"


echo
echo "Architecture:"
uname -m


# Update system

echo
echo "Updating Raspberry Pi..."

sudo apt update
sudo apt full-upgrade -y


# Basic tools

echo
echo "Installing basic tools..."

sudo apt install -y \
git \
wget \
curl \
nano \
htop \
tree \
unzip \
python3-pip \
build-essential


# Ham Radio software

echo
echo "Installing Ham Radio software..."

sudo apt install -y \
hamlib-utils \
chirp \
direwolf \
xastir \
gpsd \
gpsd-clients \
gqrx-sdr \
rtl-sdr \
gnuradio \
soapy-sdr \
soapy-sdr-module-rtlsdr \
audacity


# Digital modes

echo
echo "Installing digital mode software..."

sudo apt install -y \
wsjtx \
fldigi \
flrig


# Satellite

echo
echo "Installing satellite tools..."

sudo apt install -y \
gpredict


# Audio support

echo
echo "Installing audio tools..."

sudo apt install -y \
pulseaudio-utils \
pavucontrol


# User permissions

echo
echo "Adding USB radio permissions..."

sudo usermod -a -G dialout $USER


echo
echo "================================="
echo " Installation complete"
echo "================================="

echo
echo "Please reboot your Pi:"
echo

echo "sudo reboot"

echo
echo "Log saved:"
echo "$LOGFILE"
