#!/bin/bash

# install firmware
git clone https://github.com/whitebatman2/rtl8821CU.git
cd ./rtl8821CU
sed -i 's/I386_PC = y/I386_PC = n/' Makefile
sed -i 's/ARM_RPI = n/ARM_RPI = y/' Makefile
make
make install
modprobe 8821cu

# disable on board wifi
echo "dtoverlay=pi3-disable-wifi" >> /boot/config.txt
echo "blacklist brcmfmac" >> /etc/modprobe.d/raspi-blacklist.conf
echo "blacklist brcmutil" >> /etc/modprobe.d/raspi-blacklist.conf

# switch usb mode at boot
echo "Add the following to root crontab"
echo "@reboot /usr/sbin/usb_modeswitch -KW -v 0bda -p 1a2b >/dev/null 2>&1"
