import rpyutils
import serial
from rpyutils import printd, Level, Color, clr
from commands import *
from time import sleep


class LoRaController():
    def __init__(self, port, baudrate=57600, reset=True):
        self.device = serial.Serial(port=port, baudrate=baudrate, timeout=5*60)
        if reset:
            self.reset()
        self.hweui = self.serial_sr(CMD_GET_HWEUI)
        self.joined = False
        self.appkey = None
        self.appeui = None
        self.deveui = None
        self.nwkskey = None
        self.appskey = None
        self.devaddr = None

    def __del__(self):
        if self.device.is_open:
            self.device.close()

    # Low level serial communication
    def serial_sr(self, cmd, args=[]):
        # Add arguments
        if isinstance(args, list):
            for arg in args:
                cmd += " " + arg
        else:
            cmd += " " + args
        printd("> " + cmd, Level.DEBUG)

        if self.device.is_open:
            cmd += "\r\n"
            self.device.write(cmd.encode('utf-8'))

            return self.serial_r()
        else:
            printd(clr(Color.RED, "Attempted write to closed port"), Level.CRITICAL)

            return None

    # Test serial device
    def test(self):
        return len(self.serial_sr(CMD_GET_VERSION)) > 0

    def factory_reset(self):
        self.serial_sr(CMD_FACTORY_RESET)

    def reset(self):
        self.serial_sr(CMD_RESET)

    def serial_r(self):
        r = self.device.readline().decode('utf-8').strip()
        printd("< " + r, Level.DEBUG)

        return r

    def join_otaa(self, appkey, appeui, deveui):
        self.appkey = appkey
        self.appeui = appeui
        self.deveui = deveui

        self.serial_sr(CMD_SET_APPKEY, appkey)
        self.serial_sr(CMD_SET_APPEUI, appeui)
        self.serial_sr(CMD_SET_DEVEUI, deveui)
        self.serial_sr(CMD_JOIN_OTAA)

        if self.serial_r() == S_ACCEPTED:
            self.joined = True
            return True
        else:
            return False

    def join_abp(self, nwkskey, appskey, devaddr):
        self.nwkskey = nwkskey
        self.appskey = appskey
        self.devaddr = devaddr

        self.serial_sr(CMD_SET_NWKSKEY, nwkskey)
        self.serial_sr(CMD_SET_APPSKEY, appskey)
        self.serial_sr(CMD_SET_DEVADDR, devaddr)
        self.serial_sr(CMD_JOIN_ABP)

        if self.serial_r() == S_ACCEPTED:
            self.joined = True
            return True
        else:
            return False

    def send(self, data, port=1, ack=True):
        self.serial_sr(CMD_TX, ["cnf" if ack else "uncnf", str(port), data])
        r = self.serial_r()
        r_status = r.split(" ")[0]
        if r_status == "mac_tx_ok" or r_status == "mac_rx":
            return True
        else:
            printd("Server did not acknowledge data '" + str(data) + "' on port " + str(port), Level.DEBUG)
            return False

    def set_pwridx(self, pwridx):
        self.serial_sr(CMD_SET_PWRIDX, str(pwridx))

    def set_pwr(self, pwr):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_PWR, str(pwr))
        self.serial_sr(CMD_MAC_RESUME)

    def get_pwr(self):
        return self.serial_sr(CMD_GET_PWR)

    def set_adr(self, value):
        if self.serial_sr(CMD_SET_ADR, "on" if value else "off"):
            return True
        else:
            return False
