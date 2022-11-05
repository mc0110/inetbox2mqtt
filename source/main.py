import os

def find(name, path):
    x = False
    for files in os.listdir():
        x = x or (name in files)
    return x


if not(find("credentials.py", "/")):
    a = ""
    while a != "yes":
        print("Fill in your credentials:")
        SSID = input("SSID: ")
        print()
        Wifi_PW = input("Wifi-password: ")
        print()
        MQTT = input("MQTT-Server - IP or hostname: ")
        print()
        UName = input("Username: ")
        print()
        UPW = input("User-Password: ")
        print()
        print("Your inputs are:")
        print()
        print(f"SSID       : {SSID}")
        print(f"Wifi-PW    : {Wifi_PW}")
        print(f"MQTT-Server: {MQTT}")
        print(f"Username   : {UName}")
        print(f"User-PW    : {UPW}")
        print()
        a = input("ok for you (yes/no): ")
        print("Write credentials to disk")
        f = open("credentials.py", "w")
        f.write("from mqtt_async import config" + "\n")
        f.write("\n")
        f.write("config.server   = '"+ str(MQTT) + "'\n")
        f.write("config.ssid     = '"+ str(SSID) + "'\n")
        f.write("config.wifi_pw  = '"+ str(Wifi_PW) + "'\n")
        f.write("config.user     = '"+ str(UName) + "'\n")
        f.write("config.password = '"+ str(UPW) + "'\n")
        f.close()


import truma_serv