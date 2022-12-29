# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# TRUMA-inetbox-simulation
#
# Credentials and MQTT-server-adress must be filled
# If the mqtt-server needs authentification, this can also filled
#
# The communication with the CPplus uses ESP32-UART2 - connect (tx:GPIO17, rx:GPIO16)
#
#
#
# Version: 1.0.1
#
# change_log:
# 0.8.2 HA_autoConfig für den status error_code, clock ergänzt
# 0.8.3 encrypted credentials, including duo_control, improve the MQTT-detection
# 0.8.4 Tested with RP pico w R2040 - only UART-definition must be changed
# 0.8.5 Added support for MPU6050 implementing a 2D-spiritlevel, added board-based autoconfig for UART,
#       added config variables for activating duoControl and spirit-level features 
# 0.8.6 added board-based autoconfig for I2C bus definition
# 1.0.0 web-frontend implementation
# 1.0.1 using mqtt-commands for reboot, ota, OS-run

from mqtt_async import MQTTClient, config
import uasyncio as asyncio
# from crypto_keys import fn_crypto as crypt
from tools import set_led
from lin import Lin
from duo_control import duo_ctrl
from spiritlevel import spirit_level
# import uos
import time
from machine import UART, Pin, I2C, reset

debug_lin = False

# define global objects - important for processing
connect = None
lin = None
dc = None
sl = None

# Change the following configs to suit your environment
S_TOPIC_1       = 'service/truma/set/'
S_TOPIC_2       = 'homeassistant/status'
Pub_Prefix      = 'service/truma/control_status/' 
Pub_SL_Prefix   = 'service/spiritlevel/status/'




# Auto-discovery-function of home-assistant (HA)
HA_MODEL  = 'inetbox'
HA_SWV    = 'V03'
HA_STOPIC = 'service/truma/control_status/'
HA_CTOPIC = 'service/truma/set/'

HA_CONFIG = {
    "alive":                ['homeassistant/binary_sensor/truma/alive/config', '{"name": "truma_alive", "model": "' + HA_MODEL + '", "sw_version": "' + HA_SWV + '", "device_class": "running", "state_topic": "' + HA_STOPIC + 'alive"}'],
    "current_temp_room":    ['homeassistant/sensor/current_temp_room/config', '{"name": "truma_current_temp_room", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'current_temp_room"}'],
    "current_temp_water":   ['homeassistant/sensor/current_temp_water/config', '{"name": "truma_current_temp_water", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'current_temp_water"}'],
    "target_temp_room":     ['homeassistant/sensor/target_temp_room/config', '{"name": "truma_target_temp_room", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'target_temp_room"}'],
    "target_temp_water":    ['homeassistant/sensor/target_temp_water/config', '{"name": "truma_target_temp_water", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "device_class": "temperature", "unit_of_measurement": "°C", "state_topic": "' + HA_STOPIC + 'target_temp_water"}'],
    "energy_mix":           ['homeassistant/sensor/energy_mix/config', '{"name": "truma_energy_mix", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'energy_mix"}'],
    "el_power_level":       ['homeassistant/sensor/el_level/config', '{"name": "truma_el_power_level", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'el_power_level"}'],
    "heating_mode":         ['homeassistant/sensor/heating_mode/config', '{"name": "truma_heating_mode", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'heating_mode"}'],
    "operating_status":     ['homeassistant/sensor/operating_status/config', '{"name": "truma_operating_status", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'operating_status"}'],
    "error_code":           ['homeassistant/sensor/error_code/config', '{"name": "truma_error_code", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'error_code"}'],
    "clock":                ['homeassistant/sensor/clock/config', '{"name": "truma_clock", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "state_topic": "' + HA_STOPIC + 'clock"}'],
    "set_target_temp_room": ['homeassistant/select/target_temp_room/config', '{"name": "truma_set_roomtemp", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'target_temp_room", "options": ["0", "10", "15", "18", "20", "21", "22"] }'],
    "set_target_temp_water":['homeassistant/select/target_temp_water/config', '{"name": "truma_set_warmwater", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'target_temp_water", "options": ["0", "40", "60", "200"] }'],
    "set_heating_mode":     ['homeassistant/select/heating_mode/config', '{"name": "truma_set_heating_mode", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'heating_mode", "options": ["off", "eco", "high"] }'],
    "set_energy_mix":       ['homeassistant/select/energy_mix/config', '{"name": "truma_set_energy_mix", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'energy_mix", "options": ["none", "gas", "electricity", "mix"] }'],
    "set_el_power_level":   ['homeassistant/select/el_power_level/config', '{"name": "truma_set_el_power_level", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'el_power_level", "options": ["0", "900", "1800"] }'],
    "set_reboot":           ['homeassistant/select/set_reboot/config', '{"name": "truma_set_reboot", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'reboot", "options": ["0", "1"] }'],
    "set_os_run":           ['homeassistant/select/set_os_run/config', '{"name": "truma_set_os_run", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'os_run", "options": ["0", "1"] }'],
    "ota_update":           ['homeassistant/select/ota_update/config', '{"name": "truma_ota_update", "model": "' + HA_MODEL + '", "sw_version":"' + HA_SWV + '", "command_topic": "' + HA_CTOPIC + 'ota_update", "options": ["0", "1"] }'],
}



# Universal callback function for all subscriptions
def callback(topic, msg, retained, qos):
    topic = str(topic)
    topic = topic[2:-1]
    msg = str(msg)
    msg = msg[2:-1]
    print("Received:", topic, msg, retained, qos)
    # Command received from broker
    if topic.startswith(S_TOPIC_1):
        topic = topic[len(S_TOPIC_1):]
        if topic == "reboot":
            if msg == "1":
                print("reboot device request via mqtt")
                reset()
            return    
        if topic == "run_os":
            if msg == "1":
                print("switch to os_run -> AP-access: 192.168.4.1:80")
                connect.run_mode(0)
                reset()
            return    
        if topic == "ota_update":
            if msg == "1":
                print("update software via OTA")
                import cred
                cred.update_repo()    
            return
        if topic in lin.app.status.keys():
            print("inet-key:", topic, msg)
            try:
                lin.app.set_status(topic, msg)
            except Exception as e:
                print(exception(e))
                # send via mqtt
        elif not(dc == None):
            if topic in dc.status.keys():
                print("dc-key:", topic, msg)
#                try:
                dc.set_status(topic, msg)
#                except Exception as e:
#                    print(exception(e))
                    # send via mqtt
            else:
                print("key incl. dc is unkown")
        else:
            print("key w/o dc is unkown")
    # HA-server send ONLINE message        
    if (topic == S_TOPIC_2) and (msg == 'online'):
        print("Received HOMEASSISTANT-online message")
        await set_ha_autoconfig(client)


# Initialze the subscripted topics
async def conn_callback(client):
    print("MQTT connected")
    set_led("MQTT", True)

    # inetbox_set_commands
    await client.subscribe(S_TOPIC_1+"#", 1)
    # HA_online_command
    await client.subscribe(S_TOPIC_2, 1)


# Wifi and MQTT status
async def wifi_status(info):
    if info:
        print("Wifi connected")
    else:
        print("Wifi connection lost")
        set_led("MQTT", False)
    

# HA autodiscovery - delete all entities
async def del_ha_autoconfig(c):
    for i in HA_CONFIG.keys():
        try:
            await c.publish(HA_CONFIG[i][0], "{}", qos=1)
#            print(i,": [" + HA_CONFIG[i][0] + "payload: {}]")
        except:
            print("Publishing error in del_ha_autoconfig")
        
# HA auto discovery: define all auto config entities         
async def set_ha_autoconfig(c):
    print("set ha_autoconfig")
    for i in HA_CONFIG.keys():
        try:
            await c.publish(HA_CONFIG[i][0], HA_CONFIG[i][1], qos=1)
#            print(i,": [" + HA_CONFIG[i][0] + "payload: " + HA_CONFIG[i][1] + "]")
        except:
            print("Publishing error in set_ha_autoconfig")
        

# main publisher-loop
async def main(client):
    print("main-loop is running")
    set_led("MQTT", False)
    err_no = 1
    while err_no:
        try:
            await client.connect()
            err_no = 0
        except:
            # connect throws an error
            err_no += 1
            if err_no > 10:
            # there will be no connection possible - reboot and start web-frontend
                connect.run_mode(0)
                reset()
            
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
                print("Error in LIN status publishing")
        if not(dc == None):        
            s = dc.get_all(True)
            for key in s.keys():
                print(f'publish {key}:{s[key]}')
                try:
                    await client.publish(Pub_Prefix+key, str(s[key]), qos=1)
                except:
                    print("Error in duo_ctrl status publishing")
        if not(sl == None):        
            s = sl.get_all()
            for key in s.keys():
                print(f'publish {key}:{s[key]}')
                try:
                    await client.publish(Pub_SL_Prefix+key, str(s[key]), qos=1)
                except:
                    print("Error in spirit_level status publishing")
#Pub_SL_Prefix
# loop-count / fired every min                
        i += 1
        if not(i % 6):
            i = 0
            lin.app.status["alive"][1] = True # publish alive-heartbeat every min
            

# major ctrl loop for inetbox-communication
async def lin_loop():
    global lin
    await asyncio.sleep(1) # Delay at begin
    print("lin-loop is running")
    while True:
        lin.loop_serial()
        if not(lin.stop_async):
            await asyncio.sleep_ms(1)


# major ctrl loop for duo_ctrl_check
async def dc_loop():
    await asyncio.sleep(30) # Delay at begin
    print("duo_ctrl-loop is running")
    while True:
        dc.loop()
        await asyncio.sleep(10)

async def sl_loop():
    await asyncio.sleep(5) # Delay at begin
    print("spirit-level-loop is running")
    while True:
        sl.loop()
        #print("Angle X: " + str(sl.get_roll()) + "      Angle Y: " +str(sl.get_pitch()) )
        await asyncio.sleep_ms(100)


def run(w):
    global connect
    global lin
    global dc
    global sl
    connect = w

    # Decrypt your encrypted credentials
    # c = crypt()
    cred = connect.read_json_creds()
    print(cred)
    config.server   = cred["MQTT"]
    config.ssid     = cred["SSID"] 
    config.wifi_pw  = cred["WIFIPW"] 
    config.user     = cred["UN"] 
    config.password = cred["UPW"]

    # config.server   = c.get_decrypt_key("credentials.dat", "MQTT")
    # config.ssid     = c.get_decrypt_key("credentials.dat", "SSID") 
    # config.wifi_pw  = c.get_decrypt_key("credentials.dat", "WIFIPW") 
    # config.user     = c.get_decrypt_key("credentials.dat", "UN") 
    # config.password = c.get_decrypt_key("credentials.dat", "UPW")
    config.clean     = True
    config.keepalive = 60  # last will after 60sek off

    #Config addon features - possible to set it manually or over credentials
    #activate_duoControl  = False
    #activate_spiritlevel = False
    activate_duoControl  = (cred["ADC"] == "1")
    activate_spiritlevel = (cred["ASL"] == "1")

    config.set_last_will("service/truma/control_status/alive", "OFF", retain=True, qos=0)  # last will is important

    # hw-specific configuration
    # if ("ESP32" in uos.uname().machine):
    if (connect.platform == "esp32"):
        
        print("Found ESP32 Board, using UART2 for LIN on GPIO 16(rx), 17(tx)")
        # ESP32-specific hw-UART (#2)
        serial = UART(2, baudrate=9600, bits=8, parity=None, stop=1, timeout=3) # this is the HW-UART-no 2
        if activate_duoControl:
            print("Activate duoControl set to true, using GPIO 18,19 as input, 22,23 as output")
        if activate_spiritlevel:
            print("Activate spirit_level set to true, using I2C- on GPIO 25(scl), 26(sda)")
            # Initialize the i2c and spirit-level Object
            i2c = I2C(1, sda=Pin(26), scl=Pin(25), freq=400000)
            time.sleep(1.5)
            sl = spirit_level(i2c)
        else:
            sl = None
    #elif ("RP2040" in uos.uname().machine):
    elif (connect.platform == "rp2"):
        # RP2 pico w -specific hw-UART (#2)
        print("Found Raspberry Pico Board, using UART1 for LIN on GPIO 4(tx), 5(rx)")
        serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=3) # this is the HW-UART1 in RP2 pico w
        if activate_duoControl:
            print("Activate duoControl set to true, using GPIO 18,19 as input, 22,23 as output")
        if activate_spiritlevel:
            print("Activate spirit_level set to true, using I2C-0 on GPIO 3(scl), 2(sda)")
            # Initialize the i2c and spirit-level Object
            i2c = I2C(0, sda=Pin(2), scl=Pin(3), freq=400000)
            time.sleep(1.5)
            sl = spirit_level(i2c)
        else:
            sl = None
    else:
        print ("No compatible Board found!")
        
    # Initialize the lin-object
    lin = Lin(serial, debug_lin)
    if activate_duoControl:
        # Initialize the duo-ctrl-object
        dc = duo_ctrl()
    else:
        dc = None

    config.subs_cb  = callback
    config.connect_coro = conn_callback
    config.wifi_coro = wifi_status

    if not(dc == None):
        HA_CONFIG.update(dc.HA_DC_CONFIG)
    if not(sl == None):
        HA_CONFIG.update(sl.HA_SL_CONFIG)
        
    loop = asyncio.get_event_loop()
    client = MQTTClient(config)


    a=asyncio.create_task(main(client))
    b=asyncio.create_task(lin_loop())
    if not(dc == None):
        c=asyncio.create_task(dc_loop())
    if not(sl == None):
        d=asyncio.create_task(sl_loop())
    loop.run_forever()


