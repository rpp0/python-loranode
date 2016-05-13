import serial
from .rpyutils import printd, Level, Color, clr
from .commands import *
from time import sleep

class LoRaController():
    def __init__(self, port):
        self.port = port

        self.hweui = None
        self.appkey = None
        self.appeui = None
        self.deveui = None
        self.nwkskey = None
        self.appskey = None
        self.devaddr = None

        self.joined = False

    def join_otaa(self, appkey, appeui, deveui):
        raise NotImplementedError()

    def join_abp(self, nwkskey, appskey, devaddr):
        raise NotImplementedError()

    def send(self, data, port=1, ack=True):
        raise NotImplementedError()

    def recv(self, port=1):
        raise NotImplementedError()

    def send_p2p(self, data):
        raise NotImplementedError()

    def recv_p2p(self):
        raise NotImplementedError()

class RN2483Controller(LoRaController):
    def __init__(self, port, baudrate=57600, reset=True):
        self.device = serial.Serial(port=port, baudrate=baudrate, timeout=5*60)

        if reset:
            self.reset()

        self.hweui = self.serial_sr(CMD_GET_HWEUI)
        self.rxdelay1 = self.serial_sr(CMD_GET_RXDELAY1)
        self.rxdelay2 = self.serial_sr(CMD_GET_RXDELAY2)

    def __del__(self):
        if self.device.is_open:
            self.device.close()

    # RN2483 modem uses serial communication for commands
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

    def send_p2p(self, data):
        self.serial_sr(CMD_MAC_PAUSE)

        self.serial_sr(CMD_TX_RADIO, data)
        r = self.serial_r()

        self.serial_sr(CMD_MAC_RESUME)

    def recv_p2p(self):
        self.serial_sr(CMD_MAC_PAUSE)

        self.serial_sr(CMD_RX_RADIO, "0")
        r = self.serial_r()
        data = r[8:].strip()

        self.serial_sr(CMD_MAC_RESUME)

        return data

    def set_pwridx(self, pwridx):
        self.serial_sr(CMD_SET_PWRIDX, str(pwridx))

    def set_pwr(self, pwr):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_PWR, str(pwr))
        self.serial_sr(CMD_MAC_RESUME)

    def set_sf(self, sf):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_SF, "sf"+str(sf))
        self.serial_sr(CMD_MAC_RESUME)

    def set_bw(self, bw):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_BW, str(bw))
        self.serial_sr(CMD_MAC_RESUME)

    def set_cr(self, cr):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_CR, cr)
        self.serial_sr(CMD_MAC_RESUME)

    def set_crc(self, crc):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_CRC, crc)
        self.serial_sr(CMD_MAC_RESUME)

    def get_pwr(self):
        return self.serial_sr(CMD_GET_PWR)

    def get_sf(self):
        return self.serial_sr(CMD_GET_SF)

    def get_bw(self):
        return self.serial_sr(CMD_GET_BW)

    def get_cr(self):
        return self.serial_sr(CMD_GET_CR)

    def set_adr(self, value):
        if self.serial_sr(CMD_SET_ADR, "on" if value else "off"):
            return True
        else:
            return False

    def get_freq(self):
        return self.serial_sr(CMD_GET_FREQ)

    # TODO: Should be a serial send instead of send/receive. The OK
    # is received after the sleep duration
    def sleep(self, ms):
        self.serial_sr(CMD_SLEEP, str(ms))
        sleep(ms/1000)
