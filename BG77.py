import re
import uart_if

#TODO APN, RAI, eDRX, LTE-CAT-M
#TODO Automatic status updates from URC

#REGEX
#QCSQ
REGEX_QCSQ_SYSMODE  = 1
REGEX_QCSQ_RSSI     = 2
REGEX_QCSQ_RSRP     = 3
REGEX_QCSQ_SINR     = 4
REGEX_QCSQ_RSRQ     = 5

MINIMAL_RSSI = -100

class BG77:
    def __init__(self, interface, IP, port):
        self.interface = interface
        self.serverIP = IP
        self.serverPort = port
        self.SYSMODE = "NOSERVICE"
        self.RSSI = 0
        self.SINR = 0
        self.__regex_qcsq = re.compile("\\+QCSQ:\\s\"(\\w{1,9})\",([-]?\\d{1,3}),([-]?\\d{1,3}),([-]?\\d{1,3}),([-]?\\d{1,3})\\s*")


    def __send_command(self, command, timeout=1000, success_condition = "OK\r\n"):
        self.interface.write(command)
        if self.interface.await_response(timeout):
            print(f"ERROR: timeout, COMMAND: {command}")
            return True

        if success_condition not in self.interface.rx_string:
            print(f"ERROR: {self.interface.rx_string}, COMMAND: {command}")
            return True

        return False

    def set_radio(self, mode):
        if self.__send_command(f"AT+CFUN={mode}\r\n", 1000):
            print("Unable to set operating mode")
            return True

        return False

    def check_radio_condition(self):
        if self.__send_command("AT+QSSQ\r\n", 300):
            print("Unable to determine radio conditions")
            return True

        regex_match = self.__regex_qcsq.match(self.interface.rx_string)

        if regex_match == None:
            print("Unable to determine sysmode")
            return True
        
        self.sysmode = regex_match.group(REGEX_QCSQ_SYSMODE)

        match self.sysmode:
            case "NOSERVICE":
                self.RSSI = 0
                self.SINR = 0
            case "GSM":
                self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
                self.SINR = 0
            case "eMTC":
                self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
                self.SINR = int(regex_match.group(REGEX_QCSQ_SINR))
            case "NBIoT":
                self.RSSI = int(regex_match.group(REGEX_QCSQ_RSSI))
                self.SINR = int(regex_match.group(REGEX_QCSQ_SINR))
            case _:
                print("Unable to determine sysmode")
                return True

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
        #setup unsolicited reports
        if self.__send_command("AT+QURCCFG=\"urcport\",\"uart1\"\r\n", 300):
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

        if self.__send_command("AT+QCFG=\"nwscanmode\",3\r\n", 300):
            return True

        if self.__send_command("AT+QCFG=\"band\",0x0,0x80084,0x80084,1\r\n", 300):
            return True

        #Vodafone CZ
        if self.__send_command("AT+COPS=1,2,\"23003\"\r\n", 300):
            return True

        #APN
        if self.__send_command("AT+CGDCONT=1,\"IP\",\"lpwa.vodafone.iot\"\r\n", 300):
            return True

        return False

    def test_BG77(self):
        if self.__send_command("AT+QIACT=1\r\n", 1000):
            return True

        if self.__send_command("AT+QPING=1,\"8.8.8.8\"\r\n", 300):
            return True

        print(self.interface.rx_string)
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
    
    def send_image(self, json_string, stream, stream_length):
        if self.check_sim():
            return True
        
        if self.check_attach():
            print("Not attached to network")
            return True
    
        if self.__send_command("AT+QIACT=1\r\n", 1000):
            return True
        
        return False

    
