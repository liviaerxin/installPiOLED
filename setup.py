import glob
import subprocess
from setuptools import setup, find_packages, Extension

setup(
    name='pioled',
    version='2.0',
    description='OLEDs of SSD1306 Driver for the NVIDIA Jetson Nano',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'adafruit-blinka',
        'adafruit-circuitpython-ssd1306',
    ],
    package_data={},
    platforms=["linux", "linux2"]
)
