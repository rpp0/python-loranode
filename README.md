python-loranode
===============

Python 3 bindings for interfacing with LoRa nodes such as the RN2483, mDot, iM880A-L, and others. Currently, only the RN2483 modem is supported.


Installation
------------

Coming soon.


Examples
--------

Joining a network through Activation by Personalization (ABP) and transmitting a message:

```
lc = RN2483Controller("/dev/ttyUSB0")
if lc.join_abp("<your nwkskey>", "<your appskey>", "<your devaddr>"):
    lc.send("0001020304")
```
