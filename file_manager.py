import machine
import sdcard
import os
import time
from machine import Pin, SPI

RECORD_STACK_FILENAME = "records"
RECORDS_TOP_FILENAME = "recordstop"
SD_MOUNTPATH = "/sd"
IMAGE_DIR = "/img"

class FileManager:
    def __init__(self, miso_pin, mosi_pin, clk_pin, cs_pin):
        self.spi = SPI(0, mosi=mosi_pin, miso = miso_pin, sck = clk_pin)
        self.sd = sdcard.SDCard(self.spi, cs_pin)
        os.mount(self.sd, SD_MOUNTPATH)

    def check_files(self):
        files = os.listdir(SD_MOUNTPATH)
        
        if RECORD_STACK_FILENAME not in files:
            print(f"File {RECORD_STACK_FILENAME} not found, creating")
            open(f"{SD_MOUNTPATH}/{RECORD_STACK_FILENAME}")

        if RECORDS_TOP_FILENAME not in files:
            print(f"File {RECORDS_TOP_FILENAME} not found, creating")
            open(f"{SD_MOUNTPATH}/{RECORDS_TOP_FILENAME}")
        
    def get_random_image(self):
        files = os.listdir(f"{SD_MOUNTPATH}/{IMAGE_DIR}")

        if len(files) == 0:
            return None
        
        return files[time.ticks_ms() % len(files)]
    
    def push_record(self, image_filename):
        file = open(f"{SD_MOUNTPATH}/{RECORD_STACK_FILENAME}", "a")
        file.write(f"{time.time()};{image_filename}\r\n".encode('ascii'))

        file.close()

    def pop_records(self):
        top_file = open(f"{SD_MOUNTPATH}/{RECORDS_TOP_FILENAME}", "rw")
        stack_file = open(f"{SD_MOUNTPATH}/{RECORD_STACK_FILENAME}", "r")

        top_record = top_file.read()
        records = stack_file.read().split("\r\n")

        new_record_flag = False
        output_list = []

        for record in records:
            if new_record_flag:
                output_list.append(record)

            if top_record in record:
                new_record_flag = True

        top_file.write(f"{records[len(records-1)]}")

        top_file.close()
        stack_file.close()

        return output_list
    
    def print_all_records(self):
        file = open(f"{SD_MOUNTPATH}/{RECORD_STACK_FILENAME}", "r");
        
        print(file.read())

        file.close()
