# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# 
# For the proper functioning of the connect-library, the keys "SSID", "WIFIPW", "HOSTNAME" should be included.
# Any other keys can be added


def set_cred_json():
    import connect

    j = {
     "SSID": ["text", "SSID:", "1"],
     "WIFIPW": ["password", "Wifi passcode:", "2"],
     "MQTT": ["text", "Boker name/IP:", "3"],
     "UN": ["text", "Broker User:", "4"],
     "UPW": ["text", "Broker password:", "5"],
     "HOSTNAME": ["text", "Hostname:", "6"],
     "ADC": ["checkbox", "Addon DuoControl :", "7"],
     "ASL": ["checkbox", "Addon SpiritLevel:", "8"],
#     "OSR": ["checkbox", "OS Web:", "9"],
     }
    

    w=connect.Wifi()
    w.write_cred_json(j)


def update_repo():
    import time, os
    import mip
    #sleep to give some boards time to initialize, for example Rpi Pico W
    time.sleep(3)

    # bootloader for the whole suite
    tree = "github:mc0110/inetbox2mqtt"

    env = [
        ["/lib/", "logging.py", "/lib"],
        ["/lib/", "mqtt_async.py", "/lib"],       
        ["/lib/", "nanoweb.py", "/lib"],
        ["/lib/", "crypto_keys.py", "/lib"],
        ["/lib/", "connect.py", "/lib"],
        ["/lib/", "gen_html.py", "/lib"],
        ["/lib/", "kalman.py", "/ib"],
        ["/lib/", "web_os.py", "/lib"],
        
        ["/src/", "web_os_run.py", "/"],
        ["/src/", "cred.py", "/"],
        ["/src/", "boot.py", "/"],
        ["/src/", "main.py", "/"],
        
        ["/src/", "tools.py", "/"],
        ["/src/", "conversions.py", "/"],
        ["/src/", "lin.py", "/"],
        ["/src/", "inetboxapp.py", "/"],
        ["/src/", "truma_serv.py", "/"],
        ["/src/", "duo_control.py", "/"],
        ["/src/", "spiritlevel.py", "/"],
        ["/src/", "imu.py", "/"],
        ["/src/", "vector3d.py", "/"],
        ]


    for i in range(len(env)):
        mip.install(tree+env[i][0]+env[i][1], target= env[i][2])
