from machine import Pin

# this routine isn't nessecary - see bytes.hex(" ")
# def format_bytes(bytestring):
#     return " ".join("{:02x}".format(c) for c in bytestring)


def calculate_checksum(bytestring):
    # The checksum contains the inverted eight bit sum with carry over all data bytes or all data bytes and the protected identifier.
    cs = 0
    for b in bytestring:
        cs = (cs + b) % 0xFF

    cs = ~cs & 0xFF
    if cs == 0xFF:
        cs = 0
    return cs


def set_led(s, b):
    PIN_MAP = {
        "MQTT": 14,
        "D8"  : 12
        }
    p = Pin(PIN_MAP[s], Pin.OUT)
    if b: p.value(0)
    else: p.value(1)
    