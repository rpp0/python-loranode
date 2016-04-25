import subprocess
import os
from time import sleep
from threading import Thread


class Level:
    CRITICAL = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3
    BLOAT = 4

VERBOSITY = Level.INFO


class Color:
    GREY = '\x1b[1;37m'
    GREEN = '\x1b[1;32m'
    BLUE = '\x1b[1;34m'
    YELLOW = '\x1b[1;33m'
    RED = '\x1b[1;31m'
    MAGENTA = '\x1b[1;35m'
    CYAN = '\x1b[1;36m'


class IntervalTimer(Thread):
    def __init__(self, interval, callback, c_kwargs={}):
        Thread.__init__(self)
        self.setDaemon(True)
        self.interval = interval
        self.callback = callback
        self.c_kwargs = c_kwargs
        self.start()

    def run(self):
        while True:
            self.callback(**self.c_kwargs)
            sleep(self.interval)


def clr(color, text):
    return color + str(text) + '\x1b[0m'


def check_root():
    if not os.geteuid() == 0:
        printd(clr(Color.RED, "Run as root."), Level.CRITICAL)
        exit(1)


def set_ip_address(dev, ip):
    if subprocess.call(['ip', 'addr', 'add', ip, 'dev', dev]):
        printd("Failed to assign IP address %s to %s." % (ip, dev), Level.CRITICAL)

    if subprocess.call(['ip', 'link', 'set', 'dev', dev, 'up']):
        printd("Failed to bring device %s up." % dev, Level.CRITICAL)


def printd(string, level):
    if VERBOSITY >= level:
        print(string)


def hex_offset_to_string(byte_array):
    temp = byte_array.replace("\n", "")
    temp = temp.replace(" ", "")
    return temp.decode("hex")


def mac_to_bytes(mac):
    return ''.join(chr(int(x, 16)) for x in mac.split(':'))


def bytes_to_mac(byte_array):
    return ':'.join("{:02x}".format(ord(byte)) for byte in byte_array)


def set_debug_level(lvl):
    global VERBOSITY
    VERBOSITY = lvl


def screen(msg):
    print(chr(27) + "[2J")
    print(msg)
