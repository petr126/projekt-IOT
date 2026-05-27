from BG77 import BG77
from uart_if import interface
from file_manager import FileManager
from machine import Pin
import time
import os

TELEMETRY_INTERVAL_MS = 30 * 60 * 1000
last_telemetry_time = time.ticks_ms()


def button_irq_handle(pin):
    file_manager.push_record(file_manager.get_random_image())
    for record in new_records:
    record_data = record.split(";")
    size = os.stat(record_data[1])[6]
    print(get_image_json(record_data[0], size))
    module.send_image(get_image_json(record_data[0], size), record_data[1], size)
    time.sleep_ms(100)

def get_telemetry_json(SINR, RSRP):
    message = {
        "SINR": SINR,
        "RSRP": RSRP
    }
    return json.dumps(message)

def get_image_json(id, file_size):
    return f"{{\"type\":\"image_info\",\"id\":{id},\"size\":{file_size},\"encoding\":\"hex\"}}"

miso_pin = Pin(12)
mosi_pin = Pin(11)
clk_pin = Pin(10)
cs_pin = Pin(23, Pin.OUT, value=1)

button_pin = Pin(6, Pin.IN, Pin.PULL_UP)
button_pin.irq(handler = button_irq_handle, trigger = Pin.IRQ_FALLING)

uart = interface(115200)
module = BG77(uart, "147.229.148.105", 7001)
file_manager = FileManager(miso_pin=miso_pin, mosi_pin=mosi_pin,clk_pin=clk_pin, cs_pin=cs_pin, spi_id=1)
file_manager.check_files()

module.init_BG77()
#module.test_BG77()
module.attach_network()
#module.activate_context()

module.set_radio(0)
time.sleep_ms(1000)
module.set_radio(1)

uart.debug_print(5000)

while True:
# #    file_manager.print_all_records()
#     print("start")
module.get_radio_condition()

if time.ticks_diff(now, last_telemetry_time) >= TELEMETRY_INTERVAL_MS:
    last_telemetry_time = now
    module.send_telemetry()

    
new_records = file_manager.pop_records()
print(new_records)

#for record in new_records:
#    record_data = record.split(";")
#    size = os.stat(record_data[1])[6]
#    print(get_image_json(record_data[0], size))
#    module.send_image(get_image_json(record_data[0], size), record_data[1], size)
    
time.sleep(5)
