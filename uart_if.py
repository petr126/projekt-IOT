from machine import UART
import time
from machine import Pin

#TODO Enable/Disable callback

class interface:
    def __init__(self, uart_baudrate):
        #init uart
        self.uart = UART(0, baudrate=uart_baudrate, tx=Pin(0), rxbuf=256, rx=Pin(1), timeout = 0, timeout_char=1)
        self.rx_string = ""
        self.baudrate = uart_baudrate
        self.__byte_timeout_us = 10 * (1000000 / self.baudrate) #1000000us divided by baudrate = microseconds per byte

    def flush_rx_buffer(self):
        self.uart.flush()

    def get_n_rx_bytes(self):
        return len(self.rx_string)

    def write(self, message):
        self.flush_rx_buffer()
        self.uart.write(message)

    def await_response(self, timeout_ms):
        byte_timer = self.__byte_timeout_us
        last_n_bytes = self.uart.any()

        while timeout_ms > 0:
            if(last_n_bytes != self.uart.any()):

                while byte_timer > 0:
                    if(last_n_bytes != self.uart.any()):
                        last_n_bytes = self.uart.any()
                        byte_timer = self.__byte_timeout_us

                    byte_timer = byte_timer-1
                    time.sleep_us(1)

                rx_string = str(self.uart.read(last_n_bytes))
                return False

            timeout_ms = timeout_ms-1
            time.sleep_ms(1)
        return True
