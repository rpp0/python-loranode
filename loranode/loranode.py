import serial
import binascii
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
        raise NotImplementedError

    def join_abp(self, nwkskey, appskey, devaddr):
        raise NotImplementedError

    def send(self, data, port=1, ack=True):
        raise NotImplementedError

    def recv(self, port=1):
        raise NotImplementedError

    def send_p2p(self, data):
        raise NotImplementedError

    def recv_p2p(self):
        raise NotImplementedError


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

    def get_crc(self):
        raise NotImplementedError

    def set_adr(self, value):
        if self.serial_sr(CMD_SET_ADR, "on" if value else "off"):
            return True
        else:
            return False

    def set_prlen(self, value):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_PRLEN, value)
        self.serial_sr(CMD_MAC_RESUME)

    def get_freq(self):
        return self.serial_sr(CMD_GET_FREQ)

    def set_freq(self, freq):
        self.serial_sr(CMD_MAC_PAUSE)
        self.serial_sr(CMD_SET_FREQ, str(freq))
        self.serial_sr(CMD_MAC_RESUME)

    # TODO: Should be a serial send instead of send/receive. The OK
    # is received after the sleep duration
    def sleep(self, ms):
        self.serial_sr(CMD_SLEEP, str(ms))
        sleep(ms/1000)

    def eval(self, command):
        return self.serial_sr(command)


class E32Controller(RN2483Controller):
    def __init__(self, port, baudrate=57600, reset=True):
        self.device = serial.Serial(port=port, baudrate=baudrate, timeout=5*60)
        self.device.write(b"reset\r")

    def __del__(self):
        if self.device.is_open:
            self.device.close()

    def serial_read_until(self, delimiter):
        read_data = b""

        i = 0
        while i < len(delimiter):
            while True:
                c = self.device.read(1)
                read_data += c

                if c[0] == delimiter[i]:
                    break
                else:
                    i = 0
            i += 1

        return read_data

    def serial_sr(self, cmd, args=[]):
        # Add arguments
        if isinstance(args, list):
            for arg in args:
                cmd += " " + arg
        else:
            cmd += " " + args
        cmd += "\r"
        cmd = cmd.encode("utf-8")

        before = self.serial_read_until(b"> ")
        printd(before.decode("utf-8"), Level.DEBUG, True)

        self.device.write(cmd)
        printd(cmd.decode("utf-8"), Level.DEBUG)

        _ = self.serial_read_until(b"\n")  # Command echo
        response = self.serial_read_until(b"\n")  # Command echo
        printd(response.decode("utf-8"), Level.DEBUG, True)

# Requires latest LoPy firmware.
# To upgrade: connect pins G23 and GND, press reset and run lopyupdate.py script.
# Seemed like kind of a dirty way to communicate with the LoPy, but apparently
# this is common practice to interface with micropython. See:
# https://github.com/micropython/micropython/blob/master/tools/pyboard.py
class LoPyController(LoRaController):
    def __init__(self, port, baudrate=115200, reset=True):
        self.device = serial.Serial(port=port, baudrate=baudrate, timeout=5*60)
        self.commands_sent = 0
        self.cr = "CODING_4_8"
        self.preamble = 8
        self.sf = 7
        self.pwr = 2
        self.bw = "BW_125KHZ"
        self.freq = 868100000

        if reset:
            self.reset()

    def __del__(self):
        if self.device.is_open:
            self.device.close()

    # Interact with LoPy MicroPython VM
    def serial_sr(self, cmd):
        if self.device.is_open:
            self.serial_s(cmd)
            return self.serial_r()
        else:
            printd(clr(Color.RED, "Attempted write to closed port"), Level.CRITICAL)

            return None

    def reset(self):
        """
        Initialize the "lora" object and socket for sending and receiving data.
        """
        self.serial_s("import machine")
        self.serial_s("machine.reset()")
        sleep(5)
        self.serial_s("import pycom")
        self.serial_s("import socket")
        self.serial_s("import binascii")
        self.serial_s("from network import LoRa")
        self.serial_s("pycom.heartbeat(False)")
        self.serial_s("lora = LoRa(mode=LoRa.LORA, frequency=%d, tx_power=%d, bandwidth=LoRa.%s, sf=%d, preamble=%d, coding_rate=LoRa.%s, power_mode=LoRa.ALWAYS_ON, tx_iq=False, rx_iq=False, adr=False, public=True, tx_retries=1)" % (self.freq, self.pwr, self.bw, self.sf, self.preamble, self.cr))
        self.serial_s("s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)")
        self.serial_s("s.setblocking(True)")

        self.serial_s("lora.callback(trigger=LoRa.TX_PACKET_EVENT,handler=lambda x: x)")  # Hack to wait for completion of tx

    def serial_r(self):
        r = self.device.readline().decode('utf-8').strip()
        printd(r, Level.DEBUG)

        return r

    def serial_s(self, cmd):
        cmd += "\r\n"
        self.device.write(cmd.encode('utf-8'))
        sleep(0.05)
        self.commands_sent += 1
        if self.commands_sent >= 512:  # Workaround for very weird bug
            self.commands_sent = 0
            self.reset()

    def join_otaa(self, appkey, appeui, deveui):
        raise NotImplementedError

    def join_abp(self, nwkskey, appskey, devaddr):
        raise NotImplementedError

    def send(self, data, port=1, ack=True):
        raise NotImplementedError

    def send_p2p(self, data, wait=True):
        self.serial_s("pycom.rgbled(0x00ffff)")
        self.serial_s("s.send(binascii.unhexlify(\"" + data + "\"))")
        if wait:
            line = self.serial_r()
            while line != str(int(len(data) / 2)):
                line = self.serial_r()
        self.serial_s("pycom.rgbled(0x000000)")

    def recv_p2p(self):
        raise NotImplementedError

    def set_pwridx(self, pwridx):
        raise NotImplementedError

    def set_pwr(self, pwr):
        if pwr < 2:
            self.pwr = 2
        else:
            self.pwr = pwr
        self.reset()

    def set_sf(self, sf):
        self.sf = sf
        self.serial_s("lora.sf(%d)" % sf)

    def set_bw(self, bw):
        bw_string = "BW_125KHZ"
        if bw == 250:
            bw_string = "BW_250KHZ"
        elif bw == 500:
            bw_string = "BW_500KHZ"
        self.bw = bw_string
        self.serial_s("lora.bandwidth(LoRa.%s)" % bw_string)

    def set_cr(self, cr):
        cr_string = "CODING_4_8"
        if cr == "4/5":
            cr_string = "CODING_4_5"
        elif cr == "4/6":
            cr_string = "CODING_4_6"
        elif cr == "4/7":
            cr_string = "CODING_4_7"
        self.cr = cr_string
        self.serial_s("lora.coding_rate(LoRa.%s)" % cr_string)

    def set_crc(self, crc):
        print("Warning: setting of CRC not supported by LoPy API. Keeping enabled.")

    def get_pwr(self):
        raise NotImplementedError

    def get_sf(self):
        raise NotImplementedError

    def get_bw(self):
        raise NotImplementedError

    def get_cr(self):
        raise NotImplementedError

    def get_crc(self):
        raise NotImplementedError

    def set_adr(self, value):
        raise NotImplementedError

    def get_freq(self):
        raise NotImplementedError

    def set_freq(self, freq):
        self.freq = int(freq * 1e6)
        self.serial_s("lora.frequency(%d)" % freq)

    def set_prlen(self, value):
        self.preamble = int(value)
        self.serial_s("lora.preamble(%d)" % self.preamble)

    def eval(self, command):
        self.serial_s(command)

    def sleep(self, ms):
        raise NotImplementedError
