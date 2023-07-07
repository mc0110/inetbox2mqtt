#
#
# version 2.1.0
# slighty changes, hidden status display, typros
# modify logging structure

from tools import calculate_checksum
import conversions as cnv
import logging


class InetboxApp:

    ENERGY_MIX_MAPPING = {
        0x00: "electricity",
        0xFA: "mix",
    }
    ENERGY_MODE_MAPPING = {
        0x00: "gas",
        0x09: "mix I",
        0x12: "mix II",
    }
    ENERGY_MODE_2_MAPPING = {
        0x1: "gas/diesel",
        0x2: "electricity",
        0x3: "mix",
    }
    VENT_MODE_MAPPING = {
        0x00: "Off",
        0xB: "eco",
        0xD: "high",
        0x1: "fan 1",
        0x2: "fan 2",
        0x3: "fan 3",
        0x4: "fan 4",
        0x5: "fan 5",
        0x6: "fan 6",
        0x7: "fan 7",
        0x8: "fan 8",
        0x9: "fan 9",
        0xA: "fan 10",
    }
    AIRCON_VENT_MODE_MAPPING = {
        0x71: "low",
        0x72: "mid",
        0x73: "high",
        0x74: "night",
        0x77: "auto"
    }
    AIRCON_OPERATING_STATUS = {
        0x0: "off",
        0x4: "vent",
        0x5: "cool",
        0x6: "hot",
        0x7: "auto"
    }
    VENT_OR_OPERATING_STATUS = {
        0x01: "off",
        0x22: "on + airfan",
        0x02: "on",
        0x31: "error (?)",
        0x32: "fatal error",
        0x21: "airfan (?)",
    }
    CP_PLUS_DISPLAY_STATUS_MAPPING = {
        0xF0: "heating on",
        0x20: "standby ac on",
        0x00: "standby ac off",
        0xD0: "error",
        0x70: "fatal error",
        0x50: "boiler on",
        0x40: "boiler off",
    }
    HEATING_STATUS_MAPPING = {
        0x10: "boiler eco done",
        0x11: "boiler eco heating",
        0x30: "boiler hot done",
        0x31: "boiler hot heating",
    }
    HEATING_STATUS_2_MAPPING = {
        0x04: "normal",
        0x05: "error",
        0xFF: "fatal error (?)",
        0xFE: "normal (?)",
    }

    STATUS_BUFFER_PREAMBLE = bytes(
        [0x00, 0x00, 0x22, 0xFF, 0xFF, 0xFF, 0x54, 0x01]
    )
    STATUS_HEADER_CHECKSUM_START = 6
    STATUS_BUFFER_CHECKSUM_POSITION = 12

    STATUS_BUFFER_HEADER_RECV_STATUS = bytes([0x14, 0x33])
    STATUS_BUFFER_HEADER_TIMER = bytes([0x18, 0x3D])
    STATUS_BUFFER_HEADER_02 = bytes([0x02, 0x0D])
    STATUS_BUFFER_HEADER_03 = bytes([0x0A, 0x15])
    STATUS_BUFFER_HEADER_04 = bytes([0x12, 0x35]) #Aventa Aircon Status
    
    STATUS_BUFFER_HEADER_WRITE_STATUS = bytes([0x0C, 0x32])
    STATUS_BUFFER_HEADER_WRITE_02_STATUS = bytes([0x0C, 0x34]) #Aventa Aircon Write


# Problem is, that micropython doesn't hold the correct order of the keys (like CPython > 3.7)
# Workaround is 

    STATUS_BUFFER_TYPES = {
        
        STATUS_BUFFER_HEADER_RECV_STATUS: {
            # mapping-table: key, subject, byte-len, storage
                    1: ["dummy", 1, False],
                    2: ["checksum", 1, False],
                    3: ["target_temp_room", 2, True],
                    4: ["heating_mode", 1, True],
                    5: ["recv_status_u3", 1, False],
                    6: ["el_power_level", 2, True],
                    7: ["target_temp_water", 2, True],
                    8: ["el_power_level", 2, False],  # appears twice, we assume that it is the same
                    9: ["energy_mix", 1,True],
                   10: ["energy_mix", 1, False], # appears twice, we assume that it is the same
                   11: ["current_temp_water", 2, True],
                   12: ["current_temp_room", 2, True],
                   13: ["operating_status", 1, True],
                   14: ["error_code", 2, True],
                   15: ["recv_status_u10", 1, False],
                   16: ["recv_status_u11", 1, False],
                   17: ["recv_status_u12", 1, False],
                   18: ["recv_status_u13", 1, False],
                   19: ["recv_status_u14", 1, False],
        },
        STATUS_BUFFER_HEADER_WRITE_STATUS: {
            # mapping-table: key, mapping-key, byte-len
                    1: ["command_counter", 1, "command_counter"], 
                    2: ["checksum", 1, "checksum"],
                    3: ["target_temp_room", 2, "target_temp_room"],
                    4: ["heating_mode", 1, "heating_mode"],
                    5: ["recv_status_u3", 1, ""],
                    6: ["el_power_level", 2, "el_power_level"],
                    7: ["target_temp_water", 2, "target_temp_water"],
                    8: ["el_power_level", 2, "el_power_level"],
                    9: ["energy_mix", 1, "energy_mix"],
                   10: ["energy_mix", 1, "energy_mix"],
                   11: ["dummy", 12, ""],

        },
        STATUS_BUFFER_HEADER_WRITE_02_STATUS: {  # AVENTA-Write-Commands
            # mapping-table: key, mapping-key, byte-len
                    1: ["command_counter", 1, "command_counter"], 
                    2: ["checksum", 1, "checksum"],
                    3: ["aircon_operating_mode", 1, "aircon_operating_mode"],
                    4: ["dummy", 1, "", 0],
                    5: ["aircon_vent_mode", 1, "aircon_vent_mode"],
                    6: ["aircon_on", 1, "aircon_on"],
                    7: ["target_temp_aircon", 2, "target_temp_aircon"],
                    8: ["dummy", 2, "", 0],
                    9: ["dummy", 1, "", 0],
                    10: ["dummy", 16, "", 0],

        },
        STATUS_BUFFER_HEADER_TIMER: {
            # mapping-table: key, subject, byte-len, storage
                   1: ["dummy", 1, False],
                   2: ["checksum", 1, False],
                   3: ["timer_target_temp_room", 2, True],
                   4: ["timer_unknown2", 1, False],
                   5: ["timer_unknown3", 1, False],
                   6: ["timer_unknown4", 1, False],
                   7: ["timer_unknown5", 1, False],
                   8: ["timer_target_temp_water", 2, True],
                   9: ["timer_unknown6", 1, False],
                  10: ["timer_unknown7", 1, False],
                  11: ["timer_unknown8", 1, False],
                  12: ["timer_unknown9", 1, False],
                  13: ["timer_unknown10", 2, False],
                  14: ["timer_unknown11", 2, False],
                  15: ["timer_unknown12", 1, False],
                  16: ["timer_unknown13", 1, False],
                  17: ["timer_unknown14", 1, False],
                  18: ["timer_unknown15", 1, False],
                  19: ["timer_unknown16", 1, False],
                  20: ["timer_unknown17", 1, False],
                  21: ["timer_active", 1, True],
                  22: ["timer_start_minutes", 1, True],
                  23: ["timer_start_hours", 1, True],
                  24: ["timer_stop_minutes", 1, True],
                  25: ["timer_stop_hours", 1, True]
        },
        STATUS_BUFFER_HEADER_02: {
            # mapping-table: key, subject, byte-len, storage
                    1: ["command_counter", 1, True]
        },
        STATUS_BUFFER_HEADER_03: {
            # mapping-table: key, subject, byte-len, storage
                    1: ["dummy", 1, False],
                    2: ["checksum", 1, False],
                    3: ["clock", 2, True],
                    4: ["display", 22, False]
        },
        STATUS_BUFFER_HEADER_04: {
            # mapping-table: key, subject, byte-len, storage
                    1: ["dummy", 1, False],
                    2: ["checksum", 1, False],
                    3: ["aircon_operating_mode", 1, True],
                    4: ["dummy", 1, False],
                    5: ["aircon_vent_mode", 1, True],
                    6: ["dummy", 1, False],
                    7: ["target_temp_aircon", 2, True],
                    8: ["unknown2", 2, False],
                    9: ["unknown3", 2, False],
                    10: ["unknown4", 2, False],
                    11: ["unknown5", 2, False],
                    12: ["unknown6", 2, False]
        },
    }

    STATUS_CONVERSION_FUNCTIONS = {  # pair for reading from buffer and writing to buffer, None if writing not allowed
        "command_counter": (int, int,),
        "checksum": (int, int,),
        "alive": (str, None,),
        "target_temp_room": (
            cnv.temp_code_to_string,
            cnv.string_to_temp_code,
        ),
        "target_temp_aircon": (
            cnv.temp_code_to_string,
            cnv.string_to_temp_code,
        ),
        "aircon_operating_mode": (
            cnv.aircon_operating_mode_to_string,
            cnv.string_to_aircon_operating_mode,
        ),
        "aircon_vent_mode": (
            cnv.aircon_vent_mode_to_string,
            cnv.string_to_aircon_vent_mode,
        ),
        "heating_mode": (
            cnv.heating_mode_to_string,
            cnv.string_to_heating_mode,
        ),
        "target_temp_water": (
            cnv.temp_code_to_string,
            cnv.string_to_temp_code,
        ),
        "el_power_level": (
            cnv.el_power_code_to_string,
            cnv.string_to_el_power_code,
        ),
        "energy_mix": (
            cnv.energy_mix_code_to_string,
            cnv.string_to_energy_mix_code,
        ),
        "current_temp_room": (cnv.temp_code_to_string, None),
        "current_temp_water": (cnv.temp_code_to_string, None),
        "operating_status": (cnv.operating_status_to_string, None),
        "error_code": (cnv.error_code_to_string, None),
        "timer_target_temp_room": (
            cnv.temp_code_to_string,
            cnv.string_to_temp_code,
        ),
        "timer_target_temp_water": (
            cnv.temp_code_to_string,
            cnv.string_to_temp_code,
        ),
        "timer_active": (
            cnv.bool_to_int,
            cnv.int_to_bool,
        ),
        "timer_start_minutes": (int, int,),
        "timer_start_hours": (int, int,),
        "timer_stop_minutes": (int, int,),
        "timer_stop_hours": (int, int,),
        "clock": (cnv.clock_to_string, None,),
        "display": (str, None),
        "aircon_on": (int, int)
    }


    status = {'command_counter': [1, False], 'alive': ["OFF", True], 'target_temp_water': [0, True], 'checksum': [0, False],
              'target_temp_room': [0, True], 'heating_mode': [0, True], 'el_power_level': [0, True],
              'energy_mix': [1, True], 'current_temp_water': [0, True], 'current_temp_room': [0, True],
              'operating_status': [0, True], 'error_code': [0, False], 'aircon_operating_mode': [5, True],
              'aircon_vent_mode': [114, True], 'target_temp_aircon': [2990, True], 'aircon_on': [1, True]}

    status_updated = False

    upload_buffer = False
    upload02_buffer = False

    display_status = {}
    log = logging.getLogger(__name__)

    def __init__(self, debug):
        # when requested, set logger to debug level
        if debug:
            self.log.setLevel(logging.DEBUG)

    def map_or_debug(self, mapping, value):
        if value in mapping:
            return mapping[value]
        else:
            return f"unknown value {value:02x}"

    def handle_message(self, pid, databytes):
        try:
            # call the relevant function for the pid, if it exists ...
            {
                0x20: self.parse_command_status,
                0x21: self.parse_status_1,
                0x22: self.parse_status_2,
            }[pid](databytes)
            self.log.debug(f"Found handled message {hex(pid)}> {format_bytes(databytes)}")            
            return True
        except KeyError:
            # ... or exit with false
            return False

    def parse_command_status(self, databytes):
        data = {
            "target_temp_room": cnv.temp_code_to_decimal(
                databytes[0] | (databytes[1] & 0x0F) << 8
            ),
            "target_temp_water": cnv.temp_code_to_decimal(
                databytes[2] << 4 | (databytes[1] & 0xF0) >> 4
            ),
            "energy_mix": self.map_or_debug(self.ENERGY_MIX_MAPPING, databytes[3]),
            "energy_mode": self.map_or_debug(self.ENERGY_MODE_MAPPING, databytes[4]),
            "energy_mode_2": self.map_or_debug(
                self.ENERGY_MODE_2_MAPPING,
                databytes[5] & 0x0F,
            ),
            "vent_mode": self.map_or_debug(self.VENT_MODE_MAPPING, databytes[5] >> 4),
            "pid_20_unknown_byte_6": hex(databytes[6]),
            "pid_20_unknown_byte_7": hex(databytes[7]),
        }

        self.display_status.update(data)

    def parse_status_1(self, databytes):
        data = {
            "current_temp_room": cnv.temp_code_to_decimal(
                databytes[0] | (databytes[1] & 0x0F) << 8
            ),
            "current_temp_water": cnv.temp_code_to_decimal(
                databytes[2] << 4 | (databytes[1] & 0xF0) >> 4
            ),
            "pid_21_unknown_byte_3": hex(databytes[3]),
            "pid_21_unknown_byte_4": hex(databytes[4]),
            "vent_or_something_status": self.map_or_debug(
                self.VENT_OR_OPERATING_STATUS,
                databytes[5],
            ),
            "pid_21_unknown_byte_6": hex(databytes[6]),
            "pid_21_unknown_byte_7": hex(databytes[7]),
        }

        self.display_status.update(data)

    def parse_status_2(self, databytes):
        data = {
            "voltage": str(
                (Decimal(databytes[0]) / Decimal(10)).quantize(Decimal("0.1"))
            ),
            "cp_plus_display_status": self.map_or_debug(
                self.CP_PLUS_DISPLAY_STATUS_MAPPING,
                databytes[1],
            ),
            "heating_status": self.map_or_debug(
                self.HEATING_STATUS_MAPPING, databytes[2]
            ),
            "heating_status_2": self.map_or_debug(
                self.HEATING_STATUS_2_MAPPING, databytes[3]
            ),
            "pid_22_unknown_byte_4": hex(databytes[4]),
            "pid_22_unknown_byte_5": hex(databytes[5]),
            "pid_22_unknown_byte_6": hex(databytes[6]),
            "pid_22_unknown_byte_7": hex(databytes[7]),
        }

        self.display_status.update(data)

    def process_status_buffer_update(self, buf_id, status_buffer):
        self.log.debug(f"Status ID[{buf_id}] data: {status_buffer}")

        if not(buf_id in self.STATUS_BUFFER_TYPES.keys()):
            self.log.debug("unkown buffer type - no processing")
            return
        
        status_buffer_map = self.STATUS_BUFFER_TYPES[buf_id]
        parsed_status_buffer = {}

        val = 0
        
        keys = list(status_buffer_map.keys())
        keys.sort()       
        for key in keys:
            val_a = val
            val += status_buffer_map[key][1]
            if status_buffer_map[key][2]:
                status_key = status_buffer_map[key][0]
                if (status_key == "display"):
                    parsed_status_buffer[status_key] = [status_buffer[val_a:val].hex(" "), True]
                else:                    
                    parsed_status_buffer[status_key] = [int.from_bytes(status_buffer[val_a:val],"little"), True]
        
        self.status.update(parsed_status_buffer)
#        print(self.status)
        

    def _get_status_buffer_for_writing(self):
        # right now, we only send this one type of buffer

        if not self.upload_buffer:
            return None
        
        status_buffer_map = self.STATUS_BUFFER_TYPES[self.STATUS_BUFFER_HEADER_WRITE_STATUS]
        
        # increase output message counter
        self.status["command_counter"] = [(self.status["command_counter"][0] + 1) % 0xFF, True]
        self.status["checksum"] = [0, True]

        keys = list(status_buffer_map.keys())
        keys.sort()

        # get current status buffer contents as dict
        # routine is needed twice to calculate the correct checksum
#        try:
        binary_buffer_contents = bytearray(0)
        for key in keys:
            map_key = status_buffer_map[key][2]
            val = status_buffer_map[key][1]
            if (map_key == ""):
                s = 0
                binary_buffer_contents += s.to_bytes(val, "little")
            else:
                binary_buffer_contents += self.status[map_key][0].to_bytes(val, "little")
#         except KeyError:
#             self.updates_to_send = False
#             return None
        self.log.debug(f"result of heater status-transfer: {binary_buffer_contents.hex(" ")}")

# calculate checksum
        self.status["checksum"] = [calculate_checksum(
            (
                self.STATUS_BUFFER_PREAMBLE
                + self.STATUS_BUFFER_HEADER_WRITE_STATUS
                + binary_buffer_contents
            )[self.STATUS_HEADER_CHECKSUM_START :]  
        ), True]

#        try:
        binary_buffer_contents = bytearray(0)
        for key in keys:
            map_key = status_buffer_map[key][2]
            val = status_buffer_map[key][1]
            if (map_key == ""):
                s = 0
                binary_buffer_contents += s.to_bytes(val, "little")
            else:
                binary_buffer_contents += self.status[map_key][0].to_bytes(val, "little")
#         except KeyError:
#             self.updates_to_send = False
#             return None

        self.upload_buffer = True

        send_buffer = self.STATUS_BUFFER_PREAMBLE + self.STATUS_BUFFER_HEADER_WRITE_STATUS + binary_buffer_contents

        s = [
            bytearray([0x03, 0x10, 0x29, 0xFA, 0x00, 0x1F, 0x00, 0x1E]),
            bytearray([0x03, 0x21]) + send_buffer[0:6],
            bytearray([0x03, 0x22]) + send_buffer[6:12],
            bytearray([0x03, 0x23]) + send_buffer[12:18],
            bytearray([0x03, 0x24]) + send_buffer[18:24],
            bytearray([0x03, 0x25]) + send_buffer[24:30],
            bytearray([0x03, 0x26]) + send_buffer[30:36],
             ]
        for q in s: 
         cs = calculate_checksum(q)
         q.append(cs)
         self.log.debug(str(q.hex(" ")))
        
        return s

    def _get_status_buffer1_for_writing(self):
        # right now, we only send this one type of buffer

        if not self.upload02_buffer:
            return None
        
        status_buffer_map = self.STATUS_BUFFER_TYPES[self.STATUS_BUFFER_HEADER_WRITE_02_STATUS]
        
        # increase output message counter
        self.status["command_counter"] = [(self.status["command_counter"][0] + 1) % 0xFF, True]
        self.status["checksum"] = [0, True]

        keys = list(status_buffer_map.keys())
        keys.sort()

        # get current status buffer contents as dict
        # routine is needed twice to calculate the correct checksum
#        try:
        binary_buffer_contents = bytearray(0)
        for key in keys:
            map_key = status_buffer_map[key][2]
            val = status_buffer_map[key][1]
            if (map_key == ""):
#                s = status_buffer_map[key][3]
                s=0
                binary_buffer_contents += s.to_bytes(val, "little")
            else:
                binary_buffer_contents += self.status[map_key][0].to_bytes(val, "little")
        self.log.debug(f"result of aircon status-transfer: {binary_buffer_contents.hex(" ")}")

# calculate checksum
        self.status["checksum"] = [calculate_checksum(
            (
                self.STATUS_BUFFER_PREAMBLE
                + self.STATUS_BUFFER_HEADER_WRITE_02_STATUS
                + binary_buffer_contents
            )[self.STATUS_HEADER_CHECKSUM_START :]  
        ), True]

#        try:
        binary_buffer_contents = bytearray(0)
        for key in keys:
            map_key = status_buffer_map[key][2]
            val = status_buffer_map[key][1]
            if (map_key == ""):
                s = 0
                binary_buffer_contents += s.to_bytes(val, "little")
            else:
                binary_buffer_contents += self.status[map_key][0].to_bytes(val, "little")

        self.upload02_buffer = True

        send_buffer = self.STATUS_BUFFER_PREAMBLE + self.STATUS_BUFFER_HEADER_WRITE_02_STATUS + binary_buffer_contents

        s = [
            bytearray([0x03, 0x10, 0x29, 0xFA, 0x00, 0x1F, 0x00, 0x1E]),
            bytearray([0x03, 0x21]) + send_buffer[0:6],
            bytearray([0x03, 0x22]) + send_buffer[6:12],
            bytearray([0x03, 0x23]) + send_buffer[12:18],
            bytearray([0x03, 0x24]) + send_buffer[18:24],
            bytearray([0x03, 0x25]) + send_buffer[24:30],
            bytearray([0x03, 0x26]) + send_buffer[30:36],
             ]
        for q in s: 
         cs = calculate_checksum(q)
         q.append(cs)
         self.log.debug(str(q.hex(" ")))
        
        return s
    
    # This is the small api to the mqtt-engine
    # I changed the logic slightly, in the MAP-Definition it can be changed
    def get_status(self, key):
        # return the respective key from self.status, if it exists, and apply the conversion function
#         if key not in self.status:
#             raise KeyError
#         if key.startswith("_"):
#             return f"unknown - {self.status[key]} = {hex(self.status[key])}"
        if key not in self.STATUS_CONVERSION_FUNCTIONS:
#            self.log.warning(f"Conversion function not defined - this key {key} isn't defined?")
            raise Exception(f"Conversion function not defined - this key {key} isn't defined?")
        if self.STATUS_CONVERSION_FUNCTIONS[key] is None:
#            self.log.warning(f"Conversion function not defined - this key {key} isn't readable")
           raise Exception(f"Conversion function not defined - this key {key} isn't readable")
        return self.STATUS_CONVERSION_FUNCTIONS[key][0](self.status[key][0])


    def set_status(self, key, value):
        if key not in self.STATUS_CONVERSION_FUNCTIONS:
            raise Exception(f"Conversion function not defined - this key {key} isn't defined?")
        if self.STATUS_CONVERSION_FUNCTIONS[key] is None:
            raise Exception(f"Conversion function not defined - this key {key} isn't writeable?")
#        self.log.info(f"Setting {key} to {value}")
        self.log.debug(f"set_status: {key}:{value}")
        self.status[key] = [self.STATUS_CONVERSION_FUNCTIONS[key][1](value), True]
#        self.upload_buffer = True
        print("Status:",self.status)
        map_key = []
        for k in self.STATUS_BUFFER_TYPES[self.STATUS_BUFFER_HEADER_WRITE_STATUS]:
            map_key += [self.STATUS_BUFFER_TYPES[self.STATUS_BUFFER_HEADER_WRITE_STATUS][k][2]]
        if key in map_key:
            self.log.debug(f"heater: {key}:{value}")
            self.upload_buffer = True

        map_key = []
        for k in self.STATUS_BUFFER_TYPES[self.STATUS_BUFFER_HEADER_WRITE_02_STATUS]:
            map_key += [self.STATUS_BUFFER_TYPES[self.STATUS_BUFFER_HEADER_WRITE_02_STATUS][k][2]]
        if key in map_key:
            self.log.debug(f"aircon: {key}:{value}")
            self.upload02_buffer = True



# Status-Dump - with False, it sends all status-values
# with True it sends only a list of changed values - but reset the chance-flag
    def get_all(self, only_updates):
#        print("Status:", self.status)
        if not(only_updates):
            self.status_updated = False
            return {key: self.get_status(key) for key in self.status.keys()}
        else:
            s = {}
            for key in self.status.keys():
                self.status_updated = False
                if self.status[key][1]:
                    self.status[key][1] = False
                    self.status_updated = True
                    s.update({key: self.get_status(key)})
            return s        
        

