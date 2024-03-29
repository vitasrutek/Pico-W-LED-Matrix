import neopixel
from machine import Pin
import utime
import network
import ntptime
import ustruct
from machine import RTC
from secrets import secrets

ssid = secrets['ssid']
password = secrets['password']

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print("Připojeno k WiFi!")

# RTC setup
rtc = RTC()

# Get time from NTP
ntptime.settime()

# WS2812b LED matrix settings
ws_pin = 0
num_rows = 8
num_cols = 32
BRIGHTNESS = 0.004  # Brightness (0.004 - 1.0)
ldr = machine.ADC(26)   # For Light sensor

neoMatrix = neopixel.NeoPixel(Pin(ws_pin), num_rows * num_cols)

def set_brightness(color):
    r, g, b = color
    r = int(r * BRIGHTNESS)
    g = int(g * BRIGHTNESS)
    b = int(b * BRIGHTNESS)
    return (r, g, b)

def draw_digit(digit, start_col, color=(255, 255, 255)):
    color = set_brightness(color)

    # Numbers definition
    digits = {
        '0': [
            "######", 
            "######", 
            "##  ##", 
            "##  ##", 
            "##  ##", 
            "##  ##", 
            "######", 
            "######"
        ],
        '1': [
            "####  ", 
            "####  ", 
            "  ##  ", 
            "  ##  ", 
            "  ##  ", 
            "  ##  ", 
            "######", 
            "######"
        ],
        '2': [
            "######", 
            "######", 
            "    ##", 
            "######", 
            "######", 
            "##    ", 
            "######", 
            "######"
        ],
        '3': [
            "######", 
            "######", 
            "    ##", 
            "######", 
            "######", 
            "    ##", 
            "######", 
            "######"
        ],
        '4': [
            "##  ##", 
            "##  ##", 
            "##  ##", 
            "######", 
            "######", 
            "    ##", 
            "    ##", 
            "    ##"
        ],
        '5': [
            "######", 
            "######", 
            "##    ", 
            "######", 
            "######", 
            "    ##", 
            "######", 
            "######"
        ],
        '6': [
            "######", 
            "######", 
            "##    ", 
            "######", 
            "######", 
            "##  ##", 
            "######", 
            "######"
        ],
        '7': [
            "######", 
            "######", 
            "    ##", 
            "    ##", 
            "    ##", 
            "    ##", 
            "    ##", 
            "    ##"
        ],
        '8': [
            "######", 
            "######", 
            "##  ##", 
            "######",
            "######", 
            "##  ##", 
            "######", 
            "######"
        ],
        '9': [
            "######", 
            "##  ##", 
            "##  ##", 
            "######", 
            "######", 
            "    ##", 
            "######", 
            "######"
        ],
        'X': [
            "  ", 
            "##", 
            "##", 
            "  ", 
            "  ", 
            "##", 
            "##", 
            "  "
        ],
        'Hello': [
            "#   #                   #   ##  ",
            "#   # #### #  #   ##    ##    # ",
            "#   # #    #  #  #  #   #      #",
            "##### ###  #  #  #  #          #",
            "#   # #    #  #  #  #   #      #",
            "#   # #    #  #  #  #   ##    # ",
            "#   # #### ## ##  ##    #   ##  ",
        ],
        ':)': [
            "    #######    ",
            "  ##       ##  ",
            " ##  ## ##  ## ",
            "#             #",
            "#    #   #    #",
            " ##   ###   ## ",
            "  ##       ##  ",
            "    #######    ",
        ]
                                                
    }

    # Set for matrix
    for row in range(len(digits[digit])):
        for col in range(len(digits[digit][0])):
            matrix_index = row * num_cols + (col + start_col) % num_cols
            if (col + start_col) % 2 == 0:  # Even column
                matrix_index = ((col + start_col) % num_cols) * num_rows + row
            else:  # Odd column
                matrix_index = ((col + start_col + 1) % num_cols) * num_rows - 1 - row
            if col < num_cols and row < num_rows and digits[digit][row][col] == '#':
                neoMatrix[matrix_index] = color
            else:
                neoMatrix[matrix_index] = (0, 0, 0)

    neoMatrix.write()

def letni_cas():
    # Získej aktuální čas pomocí NTP
    ntptime.settime()
    # Získání aktuálního času
    year, month, day, hour, minute, second, _, _ = utime.localtime()
    # Definuj začátek a konec letního času
    dst_start = utime.mktime((year, 3, (31 - (5 * year // 4 + 4) % 7), 1, 0, 0, 0, 0, 0))
    dst_end = utime.mktime((year, 10, (31 - (5 * year // 4 + 1) % 7), 1, 0, 0, 0, 0, 0))
    # Zjisti, zda je aktuální čas v rozmezí začátku a konce letního času
    return dst_start < utime.mktime((year, month, day, hour, minute, second, 0, 0, 0)) < dst_end

def draw_time(hour, minute):
    # Time to hours and minutes
    hour_str = str(hour) if hour >= 10 else "0" + str(hour)
    minute_str = str(minute) if minute >= 10 else "0" + str(minute)

    # Showing hours
    draw_digit(hour_str[0], 0, color=(255, 0, 0))  # Set for first digit
    draw_digit(hour_str[1], 8, color=(255, 0, 0))  # Set for second digit

    # Semicol
    draw_digit("X", 15, color=(0, 255, 255))  # Set for semicol

    # Showing minutes
    draw_digit(minute_str[0], 18, color=(255, 0, 0))  # Set for third digit
    draw_digit(minute_str[1], 26, color=(255, 0, 0))  # Set for fourth digit

draw_digit("Hello", 0, color=(0, 255, 255))
utime.sleep (2)
draw_digit("Hello", 0, color=(0, 0, 0))
#draw_digit(":)", 0, color=(255, 0, 0))
#utime.sleep(2)

try:
    while True:
        ldr_value = ldr.read_u16()  # Read light sensor value
        if ldr_value > 59000:
            BRIGHTNESS = 0.004
        elif 50000 < ldr_value < 59000:
            BRIGHTNESS = 0.01
        elif ldr_value < 50000:
            BRIGHTNESS = 0.1
        #print('světlo je ', ldr_value, ', BRIGHTNESS je ', BRIGHTNESS)

        rok, mesic, den, _, hodiny, minuty, _, _ = rtc.datetime()   # Get actual time

        # Add 1 hour in winter time
        if letni_cas():
            hodiny += 0
        else:
            hodiny += 1
        
        formatovany_cas = "{:02d}:{:02d}".format(hodiny, minuty)

        draw_time(hodiny, minuty)   # Turn on LED for time
        utime.sleep(0.5)    # For semicol blinking
        draw_digit("X", 15, color=(255, 0, 0))
        utime.sleep(0.5)

except KeyboardInterrupt:       # Turn LED off after script interupt
    neoMatrix.fill((0, 0, 0))
    neoMatrix.write()
