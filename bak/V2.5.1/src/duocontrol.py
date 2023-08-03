
# Auto-discovery-function of home-assistant (HA)
HA_MODEL  = 'inetbox'
HA_SWV    = 'V02'
HA_STOPIC = 'service/truma/control_status/'
HA_CTOPIC = 'service/truma/set/'


class duo_ctrl:

    HA_DC_CONFIG = {
        "duo_ctrl_gas_green":    ['homeassistant/binary_sensor/duo_ctrl_gas_green/config', '{"name": "truma_duo_ctrl_gas_green", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "gas", "state_topic": "' + HA_STOPIC + 'duo_ctrl_gas_green"}'],
        "duo_ctrl_gas_red":      ['homeassistant/binary_sensor/duo_ctrl_gas_red/config', '{"name": "truma_duo_ctrl_gas_red", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "gas", "state_topic": "' + HA_STOPIC + 'duo_ctrl_gas_red"}'],
        "duo_ctrl_ctrl_I":       ['homeassistant/binary_sensor/duo_ctrl_i/config', '{"name": "truma_duo_ctrl_i", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "heat", "state_topic": "' + HA_STOPIC + 'duo_ctrl_i"}'],
        "duo_ctrl_ctrl_II":      ['homeassistant/binary_sensor/duo_ctrl_ii/config', '{"name": "truma_duo_ctrl_ii", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "heat", "state_topic": "' + HA_STOPIC + 'duo_ctrl_ii"}'],
        "set_duo_ctrl_i":        ['homeassistant/switch/duo_ctrl_i/config', '{"name": "truma_set_duo_ctrl_i", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'duo_ctrl_i"}'],
        "set_duo_ctrl_ii":       ['homeassistant/switch/duo_ctrl_ii/config', '{"name": "truma_set_duo_ctrl_ii", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'duo_ctrl_ii"}'],
        }
    
    # dict for duo control: in, pin, inverted
    DC_CONFIG = {
        "duo_ctrl_gas_green": "dc_green_pin",
        "duo_ctrl_gas_red": "dc_red_pin",
        "duo_ctrl_i": "dc_i_pin",
        "duo_ctrl_ii": "dc_ii_pin",
        }
    
    status = {}

    # build up status and initialize GPIO
    def __init__(self, pin_map):
        self.pin_map = pin_map
        for i in self.DC_CONFIG.keys():
            if self.pin_map(self.DC_CONFIG[i])[0]: # input-pins
                log.debug(f"Pin_Map: in:{self.pin_map(DC_CONFIG[i])[0]}")
                v = pin_map.get_gpio(self.DC_CONFIG[i])
                if v:
                    self.status.update({i: ["ON", True]})
                else:
                    self.status.update({i: ["OFF", True]})
            else:
                self.status.update({i:["OFF", True]})
                self.pin_map(self.DC_CONFIG[i])



    def loop(self):
        for i in self.DC_CONFIG.keys():
            # only for inputs
            if self.pin_map(DC_CONFIG[i])[0]:
                v = self.pin_map.get_gpio(self.DC_CONFIG[i])
                v_o = (self.status[i][0] == "ON")
                if v != v_o:
                    self.status[i][1] = True
                    if v:
                        self.status[i][0] = "ON"
                    else:
                        self.status[i][0] = "OFF"
                        


    # if out (in == False) then set pin - all payloads without "ON" set as "OFF"    
    def set_status(self, key, value):
        if key in self.status.keys():
            # check for output
            if not(self.DC_CONFIG[key][0]):
                self.status[key] = [value, True]
                self.pin_map.set_gpio(self.DC_CONFIG[key], (value == "ON"))
        


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
                    s.update({key: self.status[key][0]})
            return s        

