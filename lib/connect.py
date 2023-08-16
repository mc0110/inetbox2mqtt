# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# 
# Functionalities: The module establishes a Wifi connection. 
# This is done either via an STA connection or if no credentials are available,
# via an AP connection on 192.168.4.1. 
# It is possible to establish both connections in parallel.
#
# Further functionalities:
#     Reading / writing a json file for the credentials
#     Wifi-network scan
#     Reading / writing encrypted credentials from / to file


import logging
import network, os, sys, time, json
from crypto_keys import fn_crypto as crypt
from machine import reset, soft_reset, Pin
from mqtt_async2 import MQTTClient, config
import uasyncio as asyncio
from tools import PIN_MAPS, PIN_MAP


class Connect():
  
    CRED_FN = "credentials.dat"
    CRED_JSON = "cred.json"
    BOOT_CNT = "boot.dat"
    RUN_MODE = "run_mode.dat"
    client = None
    
    ap_if = None
    con_if = None
    sta_if = None
    lan_if = None
    cred_fn = None
    config = None
    fixIP = None
    dhcp = True
    hostname = ""
    scanliste = []
    platform = ""
    python = ""
    appname = "undefined"
    # mqtt-blink-time in ms
    blink_t = 100

        
    def __init__(self, hw, fn=None, debuglog=False):
        if hw == None: hw = "RP2"
        print("HW: ", hw)
        self.log = logging.getLogger(__name__)
#        self.c_coro = self.c_callback
#        self.w_coro = self.w_state
        if debuglog:
            self.log.setLevel(logging.DEBUG)
        else:    
            self.log.setLevel(logging.INFO)
        self.pin_map = hw    
        self.client = None
        self.p = PIN_MAP(PIN_MAPS[hw])
        self.wifi_flg = False
        self.mqtt_flg = False
        self.connect_log = ""
        if fn != None:
            self.cred_fn = fn
        else:    
            self.cred_fn = self.CRED_FN
            
        if not(self.CRED_JSON in os.listdir("/")):
            self.gen_cred_json()

        self.platform = str(sys.platform)
        self.platform_name = str(self.pin_map) + " " + str(sys.platform)
        self.python = '{} {} {}'.format(sys.implementation.name,'.'.join(str(s) for s in sys.implementation.version), sys.implementation._mpy)
        
        self.log.info("Detected " + self.python + " on port: " + self.platform)
        
        self.config = config
        self.set_proc()
        
        self.config.subs_cb = self.c_subscripted
        self.config.connect_coro = self.c_connected
        self.config.wifi_coro = self.w_state
        
        asyncio.create_task(self.mqtt_blink())
          
        self.p.set_led("lin_led",0)
        # self.p.set_led("mqtt_led",0)        
        if self.platform == 'rp2':
            import rp2
            rp2.country('DE')

    def mqtt_blink_ok(self):
        self.blink_t = 2000
        
    def mqtt_blink_search(self):
        self.blink_t = 100
        
    def mqtt_blink_err(self):
        self.blink_t = 300
        
    async def mqtt_blink(self):
        while 1:
            if self.blink_t != None:
                self.p.set_led("mqtt_led", True)
                await asyncio.sleep_ms(self.blink_t)
                self.p.set_led("mqtt_led", False)
                await asyncio.sleep_ms(self.blink_t)
            else:    
                self.p.set_led("mqtt_led", False)
        
        
    async def c_subscripted(self, topic, msg, retained, qos):
        self.log.debug("Received topic:" + str(topic) + " > payload: " + str(msg) + "qos: " + str(qos))
        if self.subscripted != None: await self.subscripted(topic, msg, retained, qos)

    # Initialze the connect-funct
    # define subscriptions
    async def c_connected(self, client):
        self.log.info("MQTT connected")
        self.mqtt_blink_ok()
        self.mqtt_flg = True
        if self.connected != None:
            await self.connected(client)        

    # Wifi and MQTT status
    async def w_state(self, stat):
        if stat:
            self.log.info("Interface connected: " + str(self.con_if.ifconfig()[0]))
            self.mqtt_blink_ok()
            self.wifi_flg = True
            if self.wifi_state != None: await self.wifi_state(stat) 
        else:
            self.log.info("Wifi connection lost")
            self.sta_if = None
            #self.p.set_led("mqtt_led", False)
            self.wifi_flg = False
            self.mqtt_flg = False
            self.mqtt_blink_search()
            self.connect(False)
            self.mqtt_blink_err()            
            if self.wifi_state != None: await self.wifi_state(stat) 

    def set_proc(self, wifi = None, connect = None, subscript = None):
        self.wifi_state = wifi
        self.connected = connect
        self.subscripted = subscript
        
    def gen_cred_json(self):

        j = {
         "SSID": ["text", "SSID:", "1"],
         "WIFIPW": ["password", "Wifi passcode:", "2"],
         "MQTT": ["text", "Broker name/IP:", "3"],
         "PORT": ["text", "Broker port (1883):", "4"],
         "UN": ["text", "Broker User:", "5"],
         "UPW": ["text", "Broker password:", "6"],
         "HOSTNAME": ["text", "Hostname:", "7"],
         "LAN": ["checkbox", "LAN Support :", "8"],
         "STATIC": ["checkbox", "Static IP :", "9"],
         "IP": ["text", "IP (static):", "A"],
         "TOPIC": ["text", "Topic prefix (instead of truma):", "B"],
         "ADC": ["checkbox", "Addon DuoControl :", "C"],
         "ASL": ["checkbox", "Addon SpiritLevel:", "D"],
         }
        with open(self.CRED_JSON, "w") as f: json.dump(j, f)

    def read_cred_json(self):
        with open(self.CRED_JSON, "r") as f: j=json.load(f)
        return j
    

    def set_appname(self, an):
        self.appname = an


    # run-modes (0: OS-run, 1: normal-run 2,3: ota-upload)
    def run_mode(self, set=-1):
        if set == -1:
            if (self.RUN_MODE in os.listdir("/")):
                with open(self.RUN_MODE, "r") as f: a = f.read()
                self.log.debug(f"RUN-Mode: {a}")
                return int(str(a))
            else: return 0
        if set > 0:
            if self.creds():
                with open(self.RUN_MODE, "w") as f: f.write(str(set))
                self.boot_count(10)
                self.log.info("Set RUN-Mode: " + str(set))
                return set
            else: 
                return 0
        if set == 0:
            self.log.info("Set RUN-Mode: 0 = OS-RUN")
            try:
                os.remove(self.RUN_MODE)
            except:
                pass
            return 0
        
    # boot-counts
    # ask and decrease with -1 or empty
    # 
    def boot_count(self, set=-1):
        if set == -1:
            if (self.BOOT_CNT in os.listdir("/")):
                with open(self.BOOT_CNT, "r") as f: a = f.read()
                self.log.debug("Boot tries left: " + str(a))
                a = int(str(a))
                self.boot_count(a - 1)
                return a
            else: return 0
        if set > 0:
            if self.creds():
                with open(self.BOOT_CNT, "w") as f: f.write(str(set))
                return set
            else: 
                return 0
        if set == 0:
            try:
                os.remove(self.BOOT_CNT)
            except:
                pass
            return 0

    def get_state(self):
        def get_ap(ap, id):
            if ap == None:
                return {}
            conf_s = ["mac", "ssid", "channel", "hidden", "security", "key", "hostname", "reconnects", "txpower"]
            q = {}
            for i in conf_s:
                try:
                    q.update({id + i: ap.config(i)})
                except:
                    pass
            x = ap.ifconfig()
            q.update({id + "ip": x[0]})
            q.update({id + "mask": x[1]})
            q.update({id + "gateway": x[2]})
            q.update({id + "dns": x[3]})
            return q    
        
        r = {"port": self.platform, "python": self.python}
        if self.ap_if != None:
            r["ap_state"] = "on"
            r.update(get_ap(self.ap_if,"ap_"))
        else:
            r["ap_state"] = "off"
        if self.sta_if != None:
            r["sta_state"] = "on"
            r.update(get_ap(self.sta_if,"sta_"))
        else:
            r["sta_state"] = "off"    
        r["cred_fn"] = self.creds()    
        r["cred_bak"] = self.creds_bak()
        r["run_mode"] = self.run_mode()
        r["run_mqtt"] = self.set_mqtt()
        return r


    def creds(self):
        return self.cred_fn in os.listdir("/")


    def creds_bak(self):
        a = self.cred_fn.split(".")
        return a[0]+".bak" in os.listdir("/")


    def swap_creds(self):
        if self.creds() and self.creds_bak():
            a = self.cred_fn.split(".")
            os.rename(self.cred_fn, a[0] + ".bal")
            os.rename(a[0] + ".bak", self.cred_fn)
            os.rename(a[0] + ".bal", a[0] + ".bak")


    def restore_creds(self):
        if self.creds_bak():
            a = self.cred_fn.split(".")
            os.rename(a[0] + ".bak", self.cred_fn)


    def scan(self):
        a = network.WLAN(network.STA_IF)
        time.sleep(2)
        q = a.scan()
        self.log.debug(str(q))
        return q
    
    
    def scan_html(self): # use the bootstrap-css-definitions
        a = self.scan()
        authmodes = ['Open','WEP', 'WPA-PSK', 'WPA2-PSK4', 'WPA/WPA2-PSK']
        tmp = ""
        tmp += "<div class='center'> <table class='table' cellpadding='5' cellspacing='5'><thead class='thead-light'>"
        tmp += "<tr><th>SSID</th><th>Auth</th><th>Channel</th><th>RSSIS</th><th>BSSID</th></tr></thead><tbody> \n"
        for (ssid, bssid, channel, RSSI, authmode, hidden) in a:
            tmp += "<tr><td><b>{:s}".format(ssid) + "</b></td>"
            tmp += "<td>{} {}".format(authmodes[authmode-1], hidden) + "</td>"
            tmp += "<td>{}".format(channel) + "</td>"
            tmp += "<td>{}".format(RSSI) + "</td>"
            tmp += "<td>{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*bssid) + "</td></tr> \n"
        tmp += "</tbody></table></div>"
        return tmp


    def set_ap(self, sta=-1):
        if sta == -1:  # default value returns current state
            return int((self.ap_if != None))
        self.log.info(f"set ap to: {sta}")
        self.ap_if = network.WLAN(network.AP_IF)
        # Access point definitions
        if self.platform == 'rp2':
            self.ap_if.config(ssid="Pico")
            self.ap_if.config(password="password")
        if self.platform == 'esp32':
            pass
#            self.ap_if.config(ssid="ESP32")
#            self.ap_if.config(password="password")
            
        self.ap_if.active(sta)   # activate the interface
        time.sleep(1)
        if not(sta):
            self.log.debug("AP_WLAN switched off")
            self.ap_if = None
            return 0
        else:
            self.log.info("AP enabled: " + str(self.ap_if.ifconfig()[0]))
        # print(self.get_state())
        return 1

    def connect(self, t=True):
        self.dhcp = True
        self.lan = False
        if self.creds():
            cred = self.read_json_creds()
            self.dhcp = (cred["STATIC"] != "1")
            self.lan = (cred["LAN"] == "1")
            if cred["IP"] == "":
                self.dhcp = True
            else:
                self.fixIP = cred["IP"]
        else:
            return 0
        self.log.info(f"DHCP: {self.dhcp}")        
        self.log.info(f"fixedIP: {self.fixIP}")        
        self.log.info(f"LAN: {self.lan}")        
        # set LAN connection
        if self.lan:
            self.log.debug(f"LAN Interface starting")        
            if self.set_lan(1) == 1:
                self.log.debug(f"LAN Interface started")        
                if t:
                    s = self.set_mqtt(1)
                    return s
                else:
                    return 0
            else:
                return 0
        # set wifi connection
        else:
            self.log.debug(f"WLAN Interface starting")        
            if self.set_sta(1) == 1:
                self.log.debug(f"WLAN Interface started")
                self.log.debug(f"MQTT connection starting")        
                if t:
                    s = self.set_mqtt(1)
                    return s
                else:
                    return 0
            else:
                return 0


    def set_lan(self, sta=-1):
        if sta == -1:
            return int((self.lan_if != None))
   
        if sta==1:
            if not(self.p.get_data("lan")):
                self.log.info("LAN device not defined")
                return 0
            else:
                if not(self.lan):
                    return 0
            self.log.debug("LAN device configured")
            try:
                self.log.debug("LAN-Connection")
                self.lan_if = network.LAN(mdc=Pin(self.p.get_pin("mdc")), mdio=Pin(self.p.get_pin("mdio")), ref_clk=Pin(self.p.get_pin("ref_clk")),
                                  ref_clk_mode=False, power=None, id=None, phy_addr=0, phy_type=network.PHY_KSZ8081)
            except:
                    if self.boot_count():
                        reset()
                    else:
                        soft_reset()
            try:
                time.sleep(0.5)
                self.lan_if.active(False)
            except:
                pass
            time.sleep(0.1)
            self.lan_if.active(True)
            self.log.debug(f"isconnected: {self.lan_if.isconnected()}")      # check if the station is connected to an AP

            self.log.debug(f"Mac: {self.lan_if.config('mac')}")      # get the interface's MAC address
            time.sleep(0.1)
            ipconfig = self.lan_if.ifconfig()
            self.log.info("Waiting for DHCP...")

            while (ipconfig[0]=="0.0.0.0"):
                time.sleep(0.1)
            #    lan.active(True)
                self.log.debug(f"lan.status: {self.lan_if.status()}")
                ipconfig = self.lan_if.ifconfig()

            if not(self.dhcp):
                ipconfig = self.lan_if.ifconfig()
#                    self.lan_if.ifconfig([self.fixIP])
                self.lan_if.ifconfig([self.fixIP, ipconfig[1], ipconfig[2],ipconfig[3]])
            self.con_if = self.lan_if
            self.boot_count(10)
            return 1


    def set_sta(self, sta=-1):
        if sta == -1:  # default value returns current state
            return int((self.sta_if != None))
        self.sta_if = network.WLAN(network.STA_IF)
        time.sleep(0.2)     # without delay we see on an ESP32 a system fault and reboot
        self.sta_if.active(sta)   # activate the interface
        time.sleep(0.2)     # without delay we see on an ESP32 a system fault and reboot
        if not(sta):
            self.log.debug("STA_WLAN switched off")
            self.sta_if = None
            return 0
        # sta==True / check for Creds
        cred = self.read_json_creds()
        
        if not(self.creds()):
            self.log.debug('No credentials found ...')    
            self.sta_if.active(False)
            self.sta_if = None
            return 0
        if not(cred["SSID"] != ""):
            self.log.debug('No credentials found ...')    
            self.sta_if.active(False)
            self.sta_if = None
            return 0
        c = crypt()
        ssid     = cred["SSID"] 
        wifipw  = cred["WIFIPW"] 
        self.hostname  = cred["HOSTNAME"]
        self.log.debug('Connecting with credentials to network...')
        self.sta_if.active(False)
        time.sleep(0.2)
        err = 0
        try:
            self.sta_if.active(True)
            self.sta_if.connect(ssid, wifipw)
        except:
            err = 1
        # only running on ESP32
        #if self.platform == 'esp32':
        #    self.sta_if.config(hostname = self.hostname)
        i = 0
        while not(self.sta_if.isconnected()) and not(err):
            print(".",end='')
            i += 1
            time.sleep(1)
            #self.p.toggle_led("mqtt_led")
            if i>60:
                self.log.debug("Connection couldn't be established - aborted")
                self.sta_if.active(False)
                self.sta_if = None
                if self.run_mode() == 1:
                    # boot_count() > 0, decreased
                    if self.boot_count():
                        soft_reset()
                    else:    
                        self.run_mode(0)
                        
                elif self.run_mode() > 1:  
                    soft_reset()

                # self.p.set_led("mqtt_led", 0)
                self.set_ap(1)  # sta-cred wrong, established ap-connection
                return 0  # sta-cred wrong, established ap-connection
        if err:
            self.set_ap(1)
            self.log.debug("STA connection error - couldn't be established")
            return 0
        if not(self.dhcp):
            ipconfig = self.sta_if.ifconfig()
            self.sta_if.ifconfig((self.fixIP, ipconfig[1], ipconfig[2], ipconfig[3]))
        
        self.log.debug("STA connection connected successful")
        self.log.debug(f"Mac: {self.sta_if.config('mac')}")      # get the interface's MAC address
        self.log.info("Wifi connected: " + str(self.sta_if.ifconfig()[0]))
        # self.p.set_led("mqtt_led", 1)
        self.log.debug(self.get_state())
        self.con_if = self.sta_if
        # set boot_count back, connection is realized
        self.boot_count(10)
        return 1

    def set_mqtt(self, sta=-1):
        if sta == -1:
            return (self.mqtt_flg and self.wifi_flg)
        
        if sta:
            self.log.debug("Try to open mqtt connection")
            # Decrypt your encrypted credentials
            # c = crypt()
            if self.creds():
                cred = self.read_json_creds()
                self.log.info("Found Credentials")
                self.config.server   = cred["MQTT"]
                self.config.user     = cred["UN"] 
                self.config.password = cred["UPW"]
                port = 1883
                if cred["PORT"] != "":
                    port = int(cred["PORT"])
                    self.log.info(f"MQTT Port is switched to port: {port}")
                self.config.interface = self.con_if    
                self.config.clean     = True
                self.config.keepalive = 60  # last will after 60sek off
#                self.config.set_last_will("test/alive", "OFF", retain=True, qos=0)  # last will is important for clean connect
                self.config.set_last_will("service/truma/control_status/alive", "OFF", retain=True, qos=0)  # last will is important
                self.client = MQTTClient(self.config)
                self.log.info("Start mqtt connect task")
                asyncio.create_task(self.client.connect())
                return 1
            else:
                self.log.debug("no Credentials found")
                return 0
        else:
            self.log.info("Reset Wifi and MQTT-client")
            s = network.WLAN(network.STA_IF)
            s.disconnect()
            self.mqtt_flg = False
            self.wifi_flg = False
            self.client = None                   

    # write values from the given dict (l) to crypt-file (needs crypto_keys_lib)
    def store_creds(self, l):
        self.delete_creds()
        with open(self.cred_fn, "wb") as fn:
            c = crypt()
            for key, val in l.items():
                c.fn_write_encrypt(fn, key + ":" + val)
            c.fn_write_eof_encrypt(fn)
            fn.close()

    # read json-file and move the credentials into a dict {key: value}
    def read_json_creds(self):
            JSON = self.read_cred_json()
            json = {}
            # convert JSON to json_result = {key: value}
            for i in JSON.keys():        
                json[i] = "0"
            # take results from cred-file {key: value}    
            a = self.read_creds(json)
            return a

    # take and decrypt the values from encrypted file into the given dict (l) -> return
    def read_creds(self, l):
        ro = {}
        if self.creds():
            ro = l
            c = crypt()
            for key in ro.keys():
                ro[key] = c.get_decrypt_key(self.cred_fn, key) 
        return ro   

    def delete_creds(self):
        if self.creds():
            a = self.cred_fn.split(".")
            os.rename(self.cred_fn, a[0]+".bak")
            return 0
        return 1
        


