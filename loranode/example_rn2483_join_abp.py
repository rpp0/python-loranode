#!/usr/bin/env python3

import configparser
from rpyutils import printd, Level, Color, clr, set_debug_level
from loranode import RN2483Controller

# LoRaController ABP based join and ACK test
if __name__ == "__main__":
    set_debug_level(Level.DEBUG)

    # Parse config
    cp = configparser.ConfigParser()
    cp.read('lora.cfg')
    config = cp['DEFAULT']

    # Test controller
    lc = RN2483Controller(config.get("port"))
    if lc.test():
        printd("[+] Connected to LoRa RN2483 device", Level.INFO)
    else:
        printd(clr(Color.YELLOW, "[-] Failed to get version from LoRa device"), Level.WARNING)

    # Join and send a message
    if lc.join_abp(config.get("nwkskey"), config.get("appskey"), config.get("devaddr")):
        printd("[+] Connected to gateway", Level.INFO)
        lc.set_adr(True)
        lc.set_pwr(14)
        if lc.send("AC", ack=False):
            printd(clr(Color.GREEN, "[+] Test succeeded"), Level.CRITICAL)
            del lc
            exit()

    printd(clr(Color.RED, "[-] Test failed"), Level.CRITICAL)
