from BG77 import BG77
from uart_if import interface

uart = interface(155200)
module = BG77(uart, "1.1.1.1", 1)

module.init_BG77()
module.test_BG77()