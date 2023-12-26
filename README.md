# Pico-W-LED-Matrix
MicroPython script for showing actual time on WS2812b LED matrix (32x8) with Raspberry Pi Pico W

![Screenshot](photo.jpg)

PIN GP0 (1):      DATA IN
PIN VBUS (40):    +5V
PIN GROUND (38):  GROUND

Simple script with Wifi connected Pico W device to check actual time from NTP server. Then it is showing on LED WS2812b matrix (cheap AliExpress).
Digital numbers can be easily changed with better font style, just ensure that numbers are 6 points columns and 8 point rows (6x8) for these settings.

### TODO

Light sensor
