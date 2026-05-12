from BG77 import BG77
from uart_if import interface

uart = interface(115200)
module = BG77(uart, "1.1.1.1", 1)

#uart.test()
module.init_BG77()
module.test_BG77()