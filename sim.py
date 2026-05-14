import machine
import time
import sdcard
import os



button1 = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_UP)

button1_event = False
button2_event = False

last_button1_time = 0
last_button2_time = 0

DEBOUNCE_MS = 500


def button1_irq(pin):
    global button1_event, last_button1_time

    now = time.ticks_ms()

    if time.ticks_diff(now, last_button1_time) > DEBOUNCE_MS:
        button1_event = True
        last_button1_time = now


def button2_irq(pin):
    global button2_event, last_button2_time

    now = time.ticks_ms()

    if time.ticks_diff(now, last_button2_time) > DEBOUNCE_MS:
        button2_event = True
        last_button2_time = now


button1.irq(
    trigger=machine.Pin.IRQ_FALLING,
    handler=button1_irq
)

button2.irq(
    trigger=machine.Pin.IRQ_FALLING,
    handler=button2_irq
)


# # configure RTC.ALARM0 to be able to wake the device
# rtc = machine.RTC()
# rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
#
# # set RTC.ALARM0 to fire after 10 seconds (waking the device)
# rtc.alarm(rtc.ALARM0, 10000)
#
# # put the device to sleep
# machine.deepsleep()





# LOG_FILE = "/sd/test.txt"

spi = machine.SPI(1, sck = 10, mosi= 11, miso = 12, baudrate = 1000000)
cs = machine.Pin(23, machine.Pin.OUT, value=1)

sd = sdcard.SDCard(spi, cs)

os.mount(sd, "/sd")

#print(os.listdir("/sd"))

def zapis_log():
    t = time.localtime()
    cas = "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )
   
    with open("/sd/log.txt", "a") as f:
        f.write("MOTION / " + cas + "\n")
   



def clear_file():
    with open("/sd/log.txt", "w") as f:
        f.write("")



while True:
    if button1_event:
        button1_event = False


        zapis_log()
        with open("/sd/log.txt", "r") as f:
             print(f.read())

    if button2_event:
        button2_event = False

        clear_file()
        print("reset")

    time.sleep_ms(50)
