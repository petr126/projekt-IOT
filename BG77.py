#BG77.py
#Martin Vejman

import re
import uart_if
import time
import os

#REGEX
#QCSQ
REGEX_QCSQ_SYSMODE  = 0
REGEX_QCSQ_RSSI     = 1
REGEX_QCSQ_RSRP     = 2
REGEX_QCSQ_SINR     = 3
REGEX_QCSQ_RSRQ     = 4

MINIMAL_RSSI = -100

PACKET_SIZE = 1023
CONFIRM_TIMEOUT = 10000
N_ATTEMPTS = 5

class BG77:
    def __init__(self, interface, IP, port):
        self.interface = interface
        self.serverIP = IP
        self.serverPort = port
        self.SYSMODE = "NOSERVICE"
        self.RSSI = 0
        self.SINR = 0
        self.__regex_qcsq = re.compile(r'\s*\+QCSQ:\s"(\w{1,9})"')

    def __send_command(self, command, timeout=1000, success_condition = "OK\r\n"):
        self.interface.write(command)
        if self.interface.await_response(timeout):
            print(f"ERROR: timeout, COMMAND: {command}")
            return True

        if success_condition not in self.interface.rx_string:
            print(f"ERROR: {self.interface.rx_string}, COMMAND: {command}")
            return True

        return False
    
    def __setup_PSM(self):
        #disable eDRX
        if self.__send_command("AT+CEDRXS=0\r\n", 300):
            return True
        
        return False

    def set_radio(self, mode):
        if self.__send_command(f"AT+CFUN={mode}\r\n", 1000):
            print("Unable to set operating mode")
            return True

        return False

    def check_radio_condition(self):
        if self.__send_command("AT+QCSQ\r\n", 300):
            print("Unable to determine radio conditions")
            return True

#MRDAAAAAT
        string_data = self.interface.rx_string.split(",")
        
        if "NOSERVICE" in self.interface.rx_string:
            self.SYSMODE = "NOSERVICE"
            self.RSSI = 0
            self.SINR = 0
        elif "GSM" in self.interface.rx_string:
            self.SYSMODE = "GSM"
            self.RSSI = int(string_data[REGEX_QCSQ_RSSI])
            self.SINR = 0
        elif "eMTC" in self.interface.rx_string:
            self.SYSMODE = "eMTC"
            self.RSSI = int(string_data[REGEX_QCSQ_RSSI])
            self.SINR = int(string_data[REGEX_QCSQ_SINR])
        elif "NBIoT" in self.interface.rx_string:
            self.SYSMODE = "NBIoT"
            self.RSSI = int(string_data[REGEX_QCSQ_RSSI])
            self.SINR = int(string_data[REGEX_QCSQ_SINR])
        else:
            print("Unable to determine sysmode")
            return True
        
#REGEX nefunguje, zkurvenej python, uz to nikdy nechci videt, jebat tenhle projekt	
#         print(repr(self.interface.rx_string))
# 
#         regex_match = self.__regex_qcsq.search(self.interface.rx_string)
# 
#         if regex_match == None:
#             print("Unable to determine sysmode")
#             return True
#         
#         self.SYSMODE = regex_match.group(REGEX_QCSQ_SYSMODE)
# 
#         print(f"Sysmode: {self.sysmode}")
# 
#         if self.SYSMODE == "NOSERVICE":
#             self.RSSI = 0
#             self.SINR = 0
#         elif self.SYSMODE == "GSM":
#             self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
#             self.SINR = 0
#         elif self.SYSMODE == "eMTC":
#             self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
#             self.SINR = int(regex_match.group(REGEX_QCSQ_SINR))
#         elif self.SYSMODE == "NBIoT":
#             self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
#             self.SINR = int(regex_match.group(REGEX_QCSQ_SINR))
#         else:
#             print("Unable to determine sysmode")
#             return True
# 
#         match self.sysmode:
#             case "NOSERVICE":
#                 self.RSSI = 0
#                 self.SINR = 0
#             case "GSM":
#                 self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
#                 self.SINR = 0
#             case "eMTC":
#                 self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
#                 self.SINR = int(regex_match.group(REGEX_QCSQ_SINR))
#             case "NBIoT":
#                 self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
#                 self.SINR = int(regex_match.group(REGEX_QCSQ_SINR))
#             case _:
#                 print("Unable to determine sysmode")
#                 return True

        return False

    def check_sim(self):
        if self.__send_command("AT+CPIN?\r\n", 5000):
            print("Unable to get sim status")
            return True

        if "READY\r\n" not in self.interface.rx_string:
            print(f"SIM error: {self.interface.rx_string}")
            return True

        return False
    
    def check_connection(self):
        if self.__send_command("AT+QIACT?\r\n", 5000):
            print("Unable to get sim status")
            return True

    def init_BG77(self):
        #setup URC
        if self.__send_command("AT+QURCCFG=\"urcport\",\"uart1\"\r\n", 1000):
            return True

        if self.__send_command("AT+CEREG=2\r\n", 300):
            return True

        #enable radio
        if self.set_radio(1):
            return True

        if self.check_radio_condition():
            return True

        if self.SYSMODE == "NOSERVICE":
            return True

        if self.check_sim():
            return True

        #LTE Cat-M
        if self.__send_command("AT+QCFG=\"iotopmode\",0\r\n", 300):
            return True
        
        if self.__send_command("AT+QCFG=\"band\",0x0,0x80084,0x80084,1\r\n", 300):
            return True

#         if self.__send_command("AT+QCFG=\"nwscanmode\",3,1\r\n", 300):
#             return True

        #Vodafone CZ
        if self.__send_command("AT+COPS=1,2,\"23003\"\r\n", 300):
            return True

        #APN
        if self.__send_command("AT+CGDCONT=1,\"IP\",\"lpwa.vodafone.iot\"\r\n", 300):
            return True
        
        if self.__setup_PSM():
            print("Failed to setup PSM mode")
            return True

        return False

    def test_BG77(self):
        if self.__send_command("AT+QIACT=1\r\n", 1000):
            return True

        if self.__send_command("AT+QPING=1,\"8.8.8.8\"\r\n", 300):
            return True

        print(self.interface.rx_string)
        self.interface.debug_print(2000)
        return False
    
    def attach_network(self):
        if self.__send_command(f"AT+CGATT=1\r\n", 60000):
            print("Failed to attach to network")
            return True
        return False

    def detach_network(self):
        if self.__send_command(f"AT+CGATT=0\r\n", 60000):
            print("Failed to attach to network")
            return True
        
        return False
    
    def check_attach(self):
        if self.__send_command(f"AT+CGATT?\r\n", 60000):
            print("Failed to query info")
            return True
        
        if "+CGATT: 1" in self.interface.rx_string:
            return False
        
        return True
        
    def send_telemetry(self, telemetry_string):
        if self.check_sim():
            return True
        
        if self.check_attach():
            print("Not attached to network")
            return True
    
        if self.__send_command("AT+QIACT=1\r\n", 1000):
            return True
        
        if self.__send_command(f"AT+QISEND=0,\"{self.serverIP}\",{self.serverPort},{len(telemetry_string)}\r\n", 1000, ">\r\n"):
            return True
        
        if self.__send_command((f"{telemetry_string}{b"\xA1"}").encode("ascii"), 10000, "SEND OK"):
            return True
        
        return False
    
    def send_image(self, json_string, filename, stream_length):
        file = open(filename, 'rb')
        bytes_left = os.path.getsize(filename)
        
        if self.check_sim():
            return True
        
        if self.check_attach():
            print("Not attached to network")
            return True
    
        if self.__send_command("AT+QIACT=1\r\n", 1000):
            return True
        
        #open socket
        if self.__send_command(f"AT+QIOPEN=1,0,\"UDP\",\"{self.serverIP}\",{self.serverPort},0,0\r\n", 10000, "CONNECT\r\n"):
            return True
        
        #wait for confirmation
        if self.interface.await_response(10000):
            print(f"ERROR: timeout opening socket")
            return True
        
        if "QIOPEN: 0,0" not in self.interface.rx_string:
            print(f"ERROR: opening socket failed")
            return True
                        
        if self.__send_command(f"AT+QISEND=0,{len(json_string.encode("ascii"))+1}\r\n", 1000, ">"):
            print(f"ERROR: failed to send packet")
            return True
        
        if self.__send_command((f"{json_string.encode("ascii")}{b"\xA1"}").encode("ascii"), 10000, "SEND OK"):
            print(f"ERROR: failed to send packet")
            return True
        
        #Send image
        while True:
            message = file.read(PACKET_SIZE).hex()
            attempts_left = N_ATTEMPTS
        
            if len(message) == 0:
                break
        
            #Try to send packet N_ATTEMPTS times
            while True:
                attempts_left = attempts_left - 1
                
                if attempts_left == 0:
                    return True
                
                if self.__send_command(f"AT+QISEND=0,{len(message)+1}\r\n", 1000, ">"):
                    return True
            
                self.__send_command((f"{message}{b"\xA1"}").encode("ascii"), 10000, "SEND OK")
                
                if self.interface.await_response(10000):
                    continue
                
                break
        
        return False

    
