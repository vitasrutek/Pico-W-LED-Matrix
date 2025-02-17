import neopixel
from machine import Pin
import utime
import network
import ntptime
from machine import RTC
from secrets import wifi_networks

# Funkce pro připojení k WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    for network_info in wifi_networks:
        ssid = network_info['ssid']
        password = network_info['password']
        wlan.connect(ssid, password)
        
        print(f"Připojuji se k WiFi síti: {ssid}")
        
        # Čekání na připojení
        timeout = 10  # Časový limit pro připojení
        while not wlan.isconnected() and timeout > 0:
            timeout -= 1
            utime.sleep(1)
        
        if wlan.isconnected():
            print(f"Připojeno k WiFi: {ssid}")
            return wlan
        else:
            print(f"Nepodařilo se připojit k WiFi: {ssid}")
    
    print("Nepodařilo se připojit k žádné WiFi.")
    return None

# Při spuštění se pokusíme připojit k WiFi
wlan = connect_wifi()

if wlan is None:
    print("Chyba: Nejsme připojeni k žádné WiFi. Program bude pokračovat, ale nebude možné získat čas z NTP.")
else:
    print("WiFi připojení bylo úspěšné!")

# Funkce pro zjištění, jestli je letní čas
def letni_cas():
    year, month, day, hour, minute, second, _, _ = utime.localtime()
    # Definuj začátek a konec letního času
    dst_start = utime.mktime((year, 3, (31 - (5 * year // 4 + 4) % 7), 1, 0, 0, 0, 0, 0))
    dst_end = utime.mktime((year, 10, (31 - (5 * year // 4 + 1) % 7), 1, 0, 0, 0, 0, 0))
    # Zjisti, zda je aktuální čas v rozmezí začátku a konce letního času
    return dst_start < utime.mktime((year, month, day, hour, minute, second, 0, 0, 0)) < dst_end

# Funkce pro získání aktuálního času s ohledem na letní a zimní čas
def get_time():
    # Získání aktuálního času
    year, month, day, hour, minute, second, _, _ = utime.localtime()
    
    # Oprava pro letní/zimní čas (přidání hodiny v zimním čase)
    if letni_cas():
        # Letní čas (neprovádí žádnou změnu)
        pass
    else:
        # Zimní čas (přičteme 1 hodinu)
        hour += 1

    return hour, minute


# RTC setup
rtc = RTC()

# Get time from NTP (pokud je připojeno k WiFi)
if wlan and wlan.isconnected():
    ntptime.settime()

# Zbytek skriptu pro řízení LED atd.
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

    }
    

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

def draw_time(hour, minute):
    hour_str = str(hour) if hour >= 10 else "0" + str(hour)
    minute_str = str(minute) if minute >= 10 else "0" + str(minute)

    draw_digit(hour_str[0], 0, color=(255, 0, 0))
    draw_digit(hour_str[1], 8, color=(255, 0, 0))

    draw_digit("X", 15, color=(0, 255, 255))

    draw_digit(minute_str[0], 18, color=(255, 0, 0))
    draw_digit(minute_str[1], 26, color=(255, 0, 0))

# Další funkce jako letni_cas(), a samotný kód pro zobrazení času nebo jiných informací
# ...

try:
    while True:
        ldr_value = ldr.read_u16()  # Read light sensor value
        if ldr_value > 59000:
            BRIGHTNESS = 0.004
        elif 50000 < ldr_value < 59000:
            BRIGHTNESS = 0.01
        elif ldr_value < 50000:
            BRIGHTNESS = 0.1
            
        # Připojení a aktualizace času
        if wlan:
            hodiny, minuty = get_time()
            formatovany_cas = "{:02d}:{:02d}".format(hodiny, minuty)
            draw_time(hodiny, minuty)  # Zobrazení času
        else:
            # Když není WiFi připojeno, ukáže "No WiFi"
            draw_digit("0", 0, color=(255, 0, 0))
            draw_digit("0", 8, color=(255, 0, 0))

            draw_digit("X", 15, color=(0, 255, 255))

            draw_digit("0", 18, color=(255, 0, 0))
            draw_digit("0", 26, color=(255, 0, 0))

        utime.sleep(1)

except KeyboardInterrupt:
    neoMatrix.fill((0, 0, 0))
    neoMatrix.write()

