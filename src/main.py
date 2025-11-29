from machine import Pin, SoftI2C
from machine_i2c_lcd import I2cLcd
import network
import time
import ntptime
import globals
import _thread
from webserver import start_web_server

i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, 0x27, 4, 20)


def is_dst_actief():
    tijd = time.localtime()
    jaar = tijd[0]
    maand = tijd[1]
    dag = tijd[2]
    uur = tijd[3]

    if maand == 3:
        laatste_zondag = 31
        while (
            time.localtime(time.mktime((jaar, 3, laatste_zondag, 2, 0, 0, 0, 0, 0)))[6]
            != 6
        ):
            laatste_zondag -= 1

        if dag > laatste_zondag:
            return True
        elif dag == laatste_zondag and uur >= 2:
            return True

    if 4 <= maand <= 9:
        return True

    if maand == 10:
        laatste_zondag = 31
        while (
            time.localtime(time.mktime((jaar, 10, laatste_zondag, 3, 0, 0, 0, 0, 0)))[6]
            != 6
        ):
            laatste_zondag -= 1

        if dag < laatste_zondag:
            return True
        elif dag == laatste_zondag and uur < 3:
            return True

    return False


def formateer_uur() -> tuple[str, time.struct_time]:
    dst = is_dst_actief()
    toevoegde_tijd = globals.SETTINGS["WINTERUUR"] * 3600
    if dst:
        toevoegde_tijd = globals.SETTINGS["ZOMERUUR"] * 3600

    tijd = time.localtime()
    epoch = time.mktime(tijd) + toevoegde_tijd
    tijd = time.localtime(epoch)

    tijd = time.localtime()
    uur = tijd[3]
    minuten = tijd[4]
    jaar = tijd[0]
    maand = tijd[1]
    dag = tijd[2]
    tijd_str = f"{dag:02d}-{maand:02d}-{jaar} {uur:02d}:{minuten:02d}"
    return tijd_str, tijd


lcd.putstr("connecteren met WI-FI")
print("connecteren met WI-FI")

wifi = network.WLAN(network.STA_IF)

if not wifi.isconnected():
    wifi.active(True)
    wifi.connect(globals.SETTINGS["WIFI_NAAM"], globals.SETTINGS["WIFI_WACHTWOORD"])
    while not wifi.isconnected():
        print(".", end="")
        time.sleep(0.5)

print("Geconnecteerd")
ip_info = wifi.ifconfig()
ip = ip_info[0]
print(ip)

globals.IP = ip

ntptime.settime()
uur = formateer_uur()
lcd.clear()
lcd.putstr(uur)
lcd.move_to(0, 3)
lcd.putstr(ip)
alarm_afgegaan = False

knop = Pin(4, Pin.IN, Pin.PULL_UP)
buzzer = Pin(15, Pin.OUT)
backlight_tijd = 0

_thread.start_new_thread(start_web_server, ())


while True:
    (uur_nu, uur_tuple) = formateer_uur()

    # Start alarm als het uur overeenkomt met de ingestelde alarmtijd
    if (
        globals.SETTINGS["DAGEN"][uur_tuple[6]]
        and globals.SETTINGS["ALARM"][0] == uur_tuple[3]
        and globals.SETTINGS["ALARM"][1] == uur_tuple[4]
        and uur_tuple[5] == 0
        and not alarm_afgegaan
    ):
        alarm_afgegaan = True
        buzzer.on()

    # Stop alarm bij indrukken knop, en zet backlight aan voor 5 seconden
    if knop.value() == 0:
        alarm_afgegaan = False
        lcd.backlight_on()
        backlight_tijd = time.time() + 5
        buzzer.off()

    # Knipper backlight als alarm is afgegaan
    if alarm_afgegaan:
        licht = lcd.backlight
        if licht:
            lcd.backlight_off()
        else:
            lcd.backlight_on()

    # Zet backlight uit na 5 seconden
    if time.time() > backlight_tijd:
        lcd.backlight_off()

    # Update het uur op het display als het veranderd is
    if uur_nu != uur:
        uur = uur_nu
        lcd.clear()
        lcd.putstr(uur)
        lcd.move_to(0, 2)
        lcd.putstr(
            f"Alarm: {globals.SETTINGS['ALARM'][0]:02d}:{globals.SETTINGS['ALARM'][1]:02d}"
        )
        lcd.move_to(0, 3)
        lcd.putstr(ip)
    time.sleep(0.01)
