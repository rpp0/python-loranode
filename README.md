python-loranode
===============

Python 3 bindings for interfacing with LoRa nodes such as the RN2483, mDot, iM880A-L, and others. Currently, only the Microchip RN2483 and Pycom LoPy modem are supported.


Installation
------------

Latest: use `setup.py` in this repository.
Stable: `pip install loranode`


Examples
--------

Joining a network through Activation by Personalization (ABP) and transmitting a message:

```python
from loranode import RN2483Controller

lc = RN2483Controller("/dev/ttyUSB0")
if lc.join_abp("<your nwkskey>", "<your appskey>", "<your devaddr>"):
    lc.send("0001020304")  # Expects hex input
```

Send peer to peer message:

```python
from loranode import RN2483Controller

lc = RN2483Controller("/dev/ttyUSB0")
lc.send_p2p("0001020304")
```
