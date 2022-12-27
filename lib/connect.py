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



import network, os, sys, time, json
from lib.crypto_keys import fn_crypto as crypt


class Wifi():
    
    CRED_FN = "credentials.dat"
    CRED_JSON = "cred.json"
    run_fn = "run_mode.dat"
    ap_if = None
    sta_if = None
    cred_fn = None
    hostname = ""
    scanliste = []
    platform = ""
    python = ""
        
    def __init__(self, fn=None):
        self.connect_log = ""
        if fn != None:
            self.cred_fn = fn
        else:    
            self.cred_fn = self.CRED_FN
        self.platform = str(sys.platform)
        self.python = '{} {} {}'.format(sys.implementation.name,'.'.join(str(s) for s in sys.implementation.version), sys.implementation._mpy)
        if self.platform == 'rp2':
            import rp2
            rp2.country('DE')    

    def read_cred_json(self):
        with open(self.CRED_JSON, "r") as f: j=json.load(f)
        return j
    
    def write_cred_json(self, j):
        with open(self.CRED_JSON, "w") as f: json.dump(j, f)
        return

    def connect(self):
        if (self.ap_if == None): self.set_ap(1)
        if (self.creds()): self.set_sta(1)
            
    def run_mode(self, set=-1):
        if set == -1:
            return int(self.run_fn in os.listdir("/"))
        if set == 1:
            if self.creds():
                with open(self.run_fn, "w") as f:
                    f.write("1")
                return 1
            else: 
                return 0
        if set == 0:
            os.remove(self.run_fn)
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
        if self.set_ap():
            r["ap_state"] = "on"
            r.update(get_ap(self.ap_if,"ap_"))
        else:
            r["ap_state"] = "off"
        if self.set_sta():
            r["sta_state"] = "on"
            r.update(get_ap(self.sta_if,"sta_"))
        else:
            r["sta_state"] = "off"
        r["cred_fn"] = self.creds()    
        r["cred_bak"] = self.creds_bak()
        r["run_mode"] = self.run_mode()
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
        a = None
        x = False
        if self.sta_if != None: a = self.sta_if
        if self.ap_if != None: a = self.ap_if
        if a == None:
            x = True
            a = self.set_ap(1)
            time.sleep(2)
        q = a.scan()
        if len(q):
            self.scanlist = a.scan()            
        self.scanlist = a.scan()
#        print(self.scanlist)
        if x: self.set_ap(0)
        return self.scanlist
    
    
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
            print("AP_WLAN switched off")
            self.ap_if = None
            return None
        else:
            print("Access-Point enabled")
        print(self.get_state())
        return self.ap_if


    def set_sta(self, sta=-1):  
        if sta == -1:  # default value returns current state
            return int((self.sta_if != None))
        self.sta_if = network.WLAN(network.STA_IF)
        time.sleep_ms(1)     # without delay we see on an ESP32 a system fault and reboot
        self.sta_if.active(sta)   # activate the interface
        if not(sta):
            print("STA_WLAN switched off")
            self.sta_if = None
            return None
        if not(self.creds()):
            print('No credentials found ...')    
            return None
        c = crypt()
        ssid     = c.get_decrypt_key(self.cred_fn, "SSID") 
        wifipw  = c.get_decrypt_key(self.cred_fn, "WIFIPW") 
        self.hostname  = c.get_decrypt_key(self.cred_fn, "HOSTNAME")
        print('Connecting with credentials to network...')
        self.sta_if.active(False)
        time.sleep(1)
        try:
            self.sta_if.active(True)
            self.sta_if.connect(ssid, wifipw)
        except:
            pass
        # only running on ESP32
        if self.platform == 'esp32':
            self.sta_if.config(hostname = self.hostname)
        i = 0
        while not(self.sta_if.isconnected()):
            print(".",end='')
            i += 1
            time.sleep(1)
            if i>60:
                print("Connection couldn't be established - aborted")
                self.run_mode(0)
                return self.set_ap(1)  # sta-cred wrong, established ap-connection
        print("STA connection connected successful")
        print(self.get_state())
        return self.sta_if

    # write values from the given dict (l) to crypt-file (needs crypto_keys_lib)
    def store_creds(self, l):
        self.delete_creds()
        with open(self.cred_fn, "wb") as fn:
            c = crypt()
            for key, val in l.items():
                c.fn_write_encrypt(fn, key + ":" + val)
            c.fn_write_eof_encrypt(fn)
            fn.close()

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
        


