#! /usr/bin/python3
# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# Portions copyright (c) NVIDIA 2019
# Portions copyright (c) JetsonHacks 2019

import subprocess
import time
import datetime

import adafruit_ssd1306  # This is the driver chip for the Adafruit PiOLED
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont


def get_network_interface_state(interface):
    return subprocess.check_output(
        "cat /sys/class/net/%s/operstate" % interface, shell=True
    ).decode("ascii")[:-1]


def get_ip_address(interface=None):
    if interface is None:
        cmd = "hostname -I | cut -d' ' -f1"
        return subprocess.check_output(cmd, shell=True).decode("utf-8")

    if get_network_interface_state(interface) == "down":
        return None
    cmd = (
        "ifconfig %s | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'"
        % interface
    )
    return subprocess.check_output(cmd, shell=True).decode("ascii")[:-1]


# Return a string representing the percentage of CPU in use


def get_cpu_usage():
    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    # cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'"
    
    # CPU usage in percentage https://askubuntu.com/questions/464226/how-to-get-cpu-usage-in-percentages
    # set the -n argument to 2 so that you get the second update which will be the current CPU usage. http://www.touchoftechnology.com/how-to-find-the-current-cpu-usage-in-ubuntu-not-the-average/
    cmd = "top -bn 2 -d 0.2 |grep 'Cpu(s)' | awk 'FNR==2{printf \"CPU: %.1f%%\", $2+$6+$4+$12+$14+$16}'"

    CPU = subprocess.check_output(cmd, shell=True)
    print
    return CPU


# Return a float representing the percentage of GPU in use.
# On the Jetson Nano, the GPU is GPU0


def get_gpu_usage():
    GPU = 0.0
    with open("/sys/devices/gpu.0/load", encoding="utf-8") as gpu_file:
        GPU = gpu_file.readline()
        GPU = int(GPU) / 10
    return GPU


# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# 128x32 display with hardware I2C
# Change these to the right size for your display!
WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 5

# Use for I2C.
# On the Jetson Nano
# Bus 0 (pins 28,27) is board SCL_1, SDA_1 in the jetson board definition file
# Bus 1 (pins 5, 3) is board SCL, SDA in the jetson definition file
# Default is to Bus 1; We are using Bus 0, so we need to construct the busio first ...
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = oled.width
height = oled.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

while True:

    # 0. Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load

    # 1. Draw IP address
    # Three examples here, wired, wireless and default
    # draw.text((x, top), "eth0: " + str(get_ip_address("eth0")), font=font, fill=255)
    # draw.text(
    #     (x, top + 8), "wlan0: " + str(get_ip_address("wlan0")), font=font, fill=255
    # )
    draw.text((x, top), "IP: " + str(get_ip_address()), font=font, fill=255)

    # 2. Draw GPU and CPU
    GPU = get_gpu_usage()
    CPU = get_cpu_usage()
    
    draw.text(
        (x, top + 8), "GPU: " + "{:3.1f}".format(GPU)+"%", font=font, fill=255
    )
    draw.text(
        (x + width // 2, top + 8),
        str(CPU.decode("utf-8")),
        font=font,
        fill=255,
    )

    # 2. Draw GPU Bar
    # GPU = get_gpu_usage()

    # # We draw the GPU usage as a bar graph
    # string_width, string_height = font.getsize("GPU:  ")
    # # Figure out the width of the bar
    # full_bar_width = width - (x + string_width) - 1
    # # Avoid divide by zero ...
    # if GPU == 0.0:
    #     GPU = 0.001
    # draw_bar_width = int(full_bar_width * (GPU / 100))
    # draw.text((x, top + 8), "GPU:  ", font=font, fill=255)
    # draw.rectangle(
    #     (x + string_width, top + 12, x + string_width + draw_bar_width, top + 14),
    #     outline=1,
    #     fill=1,
    # )

    # 3. Draw MemUsage
    cmd = "free -m | awk 'NR==2{printf \"Mem:  %.0f%% %s/%s M\", $3*100/$2, $3,$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True)
    draw.text((x, top + 16), str(MemUsage.decode("utf-8")), font=font, fill=255)

    # 4. Draw Disk
    # cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%dGB %s", $3,$2,$5}\''
    # Disk = subprocess.check_output(cmd, shell=True)
    # draw.text((x, top + 24), str(Disk.decode("utf-8")), font=font, fill=255)

    # 5. Draw Date
    Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((x, top + 24), str(Date), font=font, fill=255)

    # Display image.
    # Set the SSD1306 image to the PIL image we have made, then dispaly
    oled.image(image)
    oled.show()

    # 1.0 = 1 second; The divisor is the desired updates (frames) per second
    time.sleep(1.0 / 2)
