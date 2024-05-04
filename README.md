# Chicken Door Controller
For creating an automated chicken door using a Raspberry Pi Zero W, an electric drill motor (or similar), relays and a power supply.

The py program will run on the RPi, which is autolaunched with crontab (extra code included to restart the Pi if network loss).

The RPi conencts to two relays that are connected to the power supply. The controlled relays allow the power supply to feed the drill motor with positive or negative DC voltage (CW vs CCW rotation).
