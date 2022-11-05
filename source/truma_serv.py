# TRUMA-inetbox-simulation
#
# Credentials and MQTT-server-adress must be filled
# If the mqtt-server needs authentification, this can also filled
#
# The communication with the CPplus uses ESP32-UART2 - connect (tx:GPIO17, rx:GPIO16)
#
#
#import logging
# Version: 0.8.2
#
# change_log: HA_autoConfig für den status error_code, clock ergänzt
#

from mqtt_async import MQTTClient, config
import uasyncio as asyncio
from tools import set_led
from lin import Lin
from machine import UART
debug_lin       = False

# Change the following configs to suit your environment
S_TOPIC_1       = 'service/truma/set/'
S_TOPIC_2       = 'homeassistant/status'
Pub_Prefix      = 'service/truma/control_status/' 

import credentials
config.clean    = False
config.set_last_will("service/truma/control_status/alive", "OFF", retain=True, qos=0)  # last will is important

serial          = UART(2, baudrate=9600, bits=8, parity=None, stop=1, timeout=3) # this is the HW-UART-no

lin = Lin(serial, debug_lin)

HA_MODEL  = 'inetetbox'
HA_SWV    = 'V01'
HA_STOPIC = 'service/truma/control_status/'
HA_CTOPIC = 'service/truma/set/'

HA_CONFIG = {
    "truma_alive":             ['homeassistant/binary_sensor/truma/alive/config', '{"name": "truma_alive", "model": "' + HA_MODEL + '", "sw_version": "' + HA_SWV + '", "device_class": "running", "state_topic": "' + HA_STOPIC + 'alive"}'],
    "truma_current_temp_room": ['homeassistant/sensor/current_temp_room/config', '{"name": "truma_current_temp_room", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'current_temp_room"}'],
    "truma_current_temp_water":['homeassistant/sensor/current_temp_water/config', '{"name": "truma_current_temp_water", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'current_temp_water"}'],
    "truma_target_temp_room":  ['homeassistant/sensor/target_temp_room/config', '{"name": "truma_target_temp_room", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'target_temp_room"}'],
    "truma_target_temp_water": ['homeassistant/sensor/target_temp_water/config', '{"name": "truma_target_temp_water", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'target_temp_water"}'],
    "truma_energy_mix":        ['homeassistant/sensor/energy_mix/config', '{"name": "truma_energy_mix", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'energy_mix"}'],
    "el_power_level":          ['homeassistant/sensor/el_level/config', '{"name": "truma_el_power_level", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'el_power_level"}'],
    "heating_mode":            ['homeassistant/sensor/heating_mode/config', '{"name": "truma_heating_mode", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'heating_mode"}'],
    "operating_status":        ['homeassistant/sensor/operating_status/config', '{"name": "truma_operating_status", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'operating_status"}'],
    "error_code":              ['homeassistant/sensor/error_code/config', '{"name": "truma_error_code", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'error_code"}'],
    "clock":                   ['homeassistant/sensor/clock/config', '{"name": "truma_clock", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'clock"}'],
    "set_target_temp_room":    ['homeassistant/select/target_temp_room/config', '{"name": "truma_set_roomtemp", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'target_temp_room", "options": ["0", "10", "15", "18", "20", "21", "22"] }'],
    "set_target_temp_water":   ['homeassistant/select/target_temp_water/config', '{"name": "truma_set_warmwater", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'target_temp_water", "options": ["0", "40", "60", "200"] }'],
    "set_heating_mode":        ['homeassistant/select/heating_mode/config', '{"name": "truma_set_heating_mode", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'heating_mode", "options": ["off", "eco", "high"] }'],
    "set_energy_mix":          ['homeassistant/select/energy_mix/config', '{"name": "truma_set_energy_mix", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'energy_mix", "options": ["none", "gas", "electricity", "mix"] }'],
    "set_el_power_level":      ['homeassistant/select/el_power_level/config', '{"name": "truma_set_el_power_level", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'el_power_level", "options": ["0", "900", "1800"] }'],
}


def callback(topic, msg, retained, qos):
    topic = str(topic)
    topic = topic[2:-1]
    msg = str(msg)
    msg = msg[2:-1]
    print("Received:", topic, msg, retained, qos)
    if topic.startswith(S_TOPIC_1):
        topic = topic[len(S_TOPIC_1):]
        if topic in lin.app.status.keys():
            print("Key:", topic, msg)
            try:
                lin.app.set_status(topic, msg)
            except Exception as e:
                print(exception(e))
                # send via mqtt
        else:
            print("key is unkown")
    if (topic == S_TOPIC_2) and (msg == 'online'):
        print("Received HOMEASSISTANT-online message")
        await set_ha_autoconfig(client)


async def conn_callback(client):
    await client.subscribe(S_TOPIC_1+"#", 1)
    await client.subscribe(S_TOPIC_2, 1)

async def del_ha_autoconfig(c):
    for i in HA_CONFIG.keys():
        try:
            await c.publish(HA_CONFIG[i][0], "{}", qos=1)
            print(i,": [" + HA_CONFIG[i][0] + "payload: {}]")
        except:
            print("Publishing error in del_ha_autoconfig")
        
async def set_ha_autoconfig(c):
    print("set ha_autoconfig")
    for i in HA_CONFIG.keys():
        try:
            await c.publish(HA_CONFIG[i][0], HA_CONFIG[i][1], qos=1)
            print(i,": [" + HA_CONFIG[i][0] + "payload: " + HA_CONFIG[i][1] + "]")
        except:
            print("Publishing error in set_ha_autoconfig")
        

async def main(client):
    set_led("MQTT", False)
    err_no = 1
    while err_no:
        try:
            await client.connect()
            err_no = 0
        except:
            err_no = 1
    set_led("MQTT", True)
    print("connected")
    print("main-loop is running")
    await del_ha_autoconfig(client)
    await set_ha_autoconfig(client)
    
    i = 0
    while True:
        await asyncio.sleep(10) # Update every 10sec
        s =lin.app.get_all(True)
        for key in s.keys():
            print(f'publish {key}:{s[key]}')
            try:
                await client.publish(Pub_Prefix+key, str(s[key]), qos=1)
            except:
                print("Error in Status Publishing")
        i += 1
        if not(i % 6):
            i = 0
            lin.app.status["alive"][1] = True # publish alive-heartbeat every min
            

async def lin_loop():
    await asyncio.sleep(1) # Delay at begin
    print("lin-loop is running")
    while True:
        lin.loop_serial()
        if not(lin.stop_async):
            await asyncio.sleep_ms(1)


config.subs_cb  = callback
config.connect_coro = conn_callback
    
loop = asyncio.get_event_loop()
client = MQTTClient(config)
b=asyncio.create_task(lin_loop())
a=asyncio.create_task(main(client))
loop.run_forever()

