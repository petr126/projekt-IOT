from BG77 import BG77
from uart_if import interface
from file_manager import FileManager
from machine import Pin
import time

def button_irq_handle(pin):
    file_manager.push_record("test")
    time.sleep_ms(100)

miso_pin = Pin(12)
mosi_pin = Pin(11)
clk_pin = Pin(10)
cs_pin = Pin(23, Pin.OUT, value=1)

button_pin = Pin(6, Pin.IN, Pin.PULL_UP)
button_pin.irq(handler = button_irq_handle, trigger = Pin.IRQ_FALLING)

uart = interface(115200)
module = BG77(uart, "1.1.1.1", 1)
file_manager = FileManager(miso_pin=miso_pin, mosi_pin=mosi_pin,clk_pin=clk_pin, cs_pin=cs_pin, spi_id=1)
file_manager.check_files()

module.init_BG77()
module.test_BG77()

module.send_telemetry("test")


while True:
    time.sleep(10)
    #file_manager.print_all_records()
#uart.test()