#!/bin/bash
# Install the driver for the Adafruit PiOLED (3527)
# The driver for the display is a SSD1306
# for NVIDIA Jetson Nano Developer Kit, L4T
# Copyright (c) 2019 Jetsonhacks 
# MIT License

# Set our access to I2C permissions
sudo groupadd -f -r gpio
sudo usermod -aG gpio $USER
cd /tmp
git clone https://github.com/NVIDIA/jetson-gpio.git
sudo cp ~/jetson-gpio/lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d
cd -
sudo udevadm control --reload-rules && sudo udevadm trigger
sudo apt-get update
sudo apt install python3-pip python3-pil -y
# Install the new versions of Adafruit library for the SSD1306 OLED driver which uses CircuitPython
sudo pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-ssd1306
# We should be able to access the PiOLED now
# Note that we may have to reboot for the i2c change to take effect




