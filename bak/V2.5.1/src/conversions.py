# from decimal import Decimal

def bool_to_int(value):
    return int(value)

def int_to_bool(value):
    return bool(value)

# convert two-byte representation of temperature to a Decimal
def temp_code_to_decimal(bytestring) -> str:
    if bytestring == 0xAAA or bytestring == 0xAAAA or bytestring == 0x0000:
        return "0"
#    return str((Decimal(bytestring) / Decimal(10) - Decimal(273)).quantize(Decimal("0.1")))
    return str(round((bytestring / 10.0 - 273.), 1))


# convert two-byte representation of temperature to a str
def temp_code_to_string(bytestring) -> str:
    return str(temp_code_to_decimal(bytestring))

# inverse function of the above, observe exception for None
def decimal_to_temp_code(decimal) -> int:
    if (decimal is None) or (decimal < 5):
        # return 0xAAA
        return 0x00
    return int((decimal + 273.0) * 10.0)

def string_to_temp_code(string):
    return decimal_to_temp_code(float(string))

# error status is 1 if a warning exists, rest of values unknown yet
def operating_status_to_string(operating_status):
    if operating_status == 0:
        return "Off"
    elif operating_status == 1:
        return "WARNING"
    elif operating_status == 4:
        return "start/cool down"
    elif operating_status == 5:
        return "On(5)"
    elif operating_status == 6:
        return "On(6)"
    elif operating_status == 7:
        return "On(7)"
    else:
        return f"On({operating_status})"

# error code is two bytes, first byte * 100 + second byte is the error code
def error_code_to_string(error_code_bytes):
    error_code = int(error_code_bytes/256) * 100 + (error_code_bytes % 256)
    return str(error_code)

# Electric heating power level is stored as a two-byte integer and has
# the values 0, 900, or 1800
def el_power_code_to_string(el_power_code):
    return str(el_power_code)

# inverse of the above
def string_to_el_power_code(string):
    code = int(string)
    if code == 0 or code == 900 or code == 1800:
        return code
    else:
        raise ValueError(f"Invalid electric heating power code: {code}")

# energy mix is stored in a byte, with the lowest bit indicating
# whether gas is used and the second lowest bit indicating whether
# electricity is used
energy_mix_mapping = {
    0b00: "none",
    0b01: "gas",
    0b10: "electricity",
    0b11: "mix",
}

def energy_mix_code_to_string(energy_mix_code):
    return energy_mix_mapping[energy_mix_code]

# inverse of the above
def string_to_energy_mix_code(string):
    for code, name in energy_mix_mapping.items():
        if name == string:
            return code
    raise ValueError(f"Invalid energy mix code: {string}")

def heating_mode_to_string(heating_mode):
    if heating_mode == 0:
        return "off"
    elif heating_mode == 1:
        return "eco"
    elif heating_mode == 10:
        return "high"
    else:
        return f"UNKNOWN ({heating_mode})"
    
# inverse of the above
def string_to_heating_mode(string):
    if string == "off":
        return 0
    elif string == "eco":
        return 1
    elif string == "high":
        return 10
    else:
        raise ValueError(f"Invalid heating mode: {string}")

def aircon_vent_mode_to_string(aircon_vent_mode):
    if aircon_vent_mode == 113:
        return "low"
    elif aircon_vent_mode == 114:
        return "mid"
    elif aircon_vent_mode == 115:
        return "high"
    elif aircon_vent_mode == 116:
        return "night"
    elif aircon_vent_mode == 119:
        return "auto"
    else:
        return f"UNKNOWN ({aircon_vent_mode})"
    
# inverse of the above
def string_to_aircon_vent_mode(string):
    if string == "low":
        return 113
    elif string == "mid":
        return 114
    elif string == "high":
        return 115
    elif string == "night":
        return 116
    elif string == "auto":
        return 119
    else:
        raise ValueError(f"Invalid heating mode: {string}")

def aircon_operating_mode_to_string(aircon_operating_mode):
    if aircon_operating_mode == 0:
        return "off"
    elif aircon_operating_mode == 4:
        return "vent"
    elif aircon_operating_mode == 5:
        return "cool"
    elif aircon_operating_mode == 6:
        return "hot"
    elif aircon_operating_mode == 7:
        return "auto"
    else:
        return f"UNKNOWN ({aircon_operating_mode})"
    
# inverse of the above
def string_to_aircon_operating_mode(string):
    if string == "off":
        return 0
    elif string == "vent":
        return 4
    elif string == "cool":
        return 5
    elif string == "hot":
        return 6
    elif string == "auto":
        return 7
    else:
        raise ValueError(f"Invalid aircon operating mode: {string}")

def clock_to_string(clock):
    m = int(clock / 256)
    h = int(clock - (m * 256))
    return f"{h:02}:{m:02}"
            
