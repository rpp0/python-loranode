#!/usr/bin/env python3

import struct
from rpyutils import printd, Level, Color, clr, set_debug_level
from threading import Thread, Lock
from loranode import RN2483Controller
from time import sleep

class ReceiverThread(Thread):
    def __init__(self, mutex):
        Thread.__init__(self)
        self.setDaemon(True)
        self.lc = RN2483Controller("/dev/ttyUSB0")
        self.mutex = mutex

    def run(self):
        while True:
            r = self.lc.recv_p2p()

            self.mutex.acquire() # Do not let prints occur simultaneously
            printd(clr(Color.BLUE, "RECV: " + r), Level.INFO)
            self.mutex.release()

class TransmitterThread(Thread):
    def __init__(self, mutex):
        Thread.__init__(self)
        self.setDaemon(True)
        self.lc = RN2483Controller("/dev/ttyUSB1")
        self.mutex = mutex
        self.counter = 0

    def run(self):
        while True:
            data = struct.pack(">I", self.counter).hex()
            self.counter += 1

            self.mutex.acquire()
            printd(clr(Color.GREEN, "SEND: " + data), Level.INFO)
            self.mutex.release()

            r = self.lc.send_p2p(data)
            sleep(5)

# LoRaController peer-to-peer test, assuming two devices at /dev/ttyUSB0 and
# /dev/ttyUSB1
if __name__ == "__main__":
    set_debug_level(Level.DEBUG)

    m = Lock()
    r = ReceiverThread(m)
    r.start()
    t = TransmitterThread(m)
    t.start()

    r.join()
    t.join()
