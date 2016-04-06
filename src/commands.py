# This command resets the module’s configuration data and user EEPPROM to
# factory # default values and restarts the module. After factoryRESET, the
# RN2483 module will automatically reset and all configuration parameters are
# restored to factory default values.
CMD_FACTORY_RESET = "sys factoryRESET"

CMD_RESET = "sys reset"
CMD_GET_VERSION = "sys get ver"
CMD_GET_HWEUI = "sys get hweui"

CMD_SET_APPKEY = "mac set appkey"
CMD_SET_APPEUI = "mac set appeui"
CMD_SET_DEVEUI = "mac set deveui"
CMD_JOIN_OTAA = "mac join otaa"

CMD_SET_NWKSKEY = "mac set nwkskey"
CMD_SET_APPSKEY = "mac set appskey"
CMD_SET_DEVADDR = "mac set devaddr"
CMD_JOIN_ABP = "mac join abp"

CMD_MAC_PAUSE = "mac pause"
CMD_MAC_RESUME = "mac resume"
CMD_SET_ADR = "mac set adr"
CMD_TX = "mac tx"
CMD_TX_RADIO = "radio tx"
CMD_RX_RADIO = "radio rx"

CMD_GET_PWR = "radio get pwr"
CMD_GET_PWRIDX = "mac get pwridx"
CMD_SET_PWR = "radio set pwr"
CMD_SET_PWRIDX = "mac set pwridx"

# Status codes
S_ACCEPTED = "accepted"
S_DENIED = "denied"
S_OK = "ok"
