# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# 
# For the proper functioning of the connect-library, the keys "SSID", "WIFIPW", "HOSTNAME" should be included.
# Any other keys can be added

# 
# def set_cred_json():
#     import json
#     CRED_JSON = "cred.json"
# 
#     j = {
#      "SSID": ["text", "SSID:", "1"],
#      "WIFIPW": ["password", "Wifi passcode:", "2"],
#      "MQTT": ["text", "Broker name/IP:", "3"],
#      "UN": ["text", "Broker User:", "4"],
#      "UPW": ["text", "Broker password:", "5"],
#      "HOSTNAME": ["text", "Hostname:", "6"],
#      "ADC": ["checkbox", "Addon DuoControl :", "7"],
#      "ASL": ["checkbox", "Addon SpiritLevel:", "8"],
# #     "OSR": ["checkbox", "OS Web:", "9"],
#      }
#     with open(CRED_JSON, "w") as f: json.dump(j, f)
# 

def update_repo():
    import mip
    #sleep to give some boards time to initialize, for example Rpi Pico W

    # bootloader for the whole suite
    tree = "github:mc0110/inetbox2mqtt"

    env = [
        ["/lib/", "connect.py", "/lib"],
        ["/lib/", "gen_html.py", "/lib"],
        ["/lib/", "kalman.py", "/lib"],
        ["/lib/", "web_os.py", "/lib"],        
        ["/lib/", "web_os_main.py", "/lib"],
           
        ["/src/", "tools.py", "/"],
        ["/src/", "conversions.py", "/"],
        ["/src/", "lin.py", "/"],
        ["/src/", "inetboxapp.py", "/"],
        ["/src/", "main.py", "/"],
        ["/src/", "main1.py", "/"],
        ["/src/", "duo_control.py", "/"],
        ["/src/", "spiritlevel.py", "/"],
        ["/src/", "imu.py", "/"],
        ["/src/", "vector3d.py", "/"],
        ["/src/", "cred.py", "/"],
        ]


    for i in range(len(env)):
        errno = 1
        while errno and errno>1:
            try:
                mip.install(tree+env[i][0]+env[i][1], target= env[i][2])
                errno = 0
            except:
                errno = 2
            s = env[i][1]
            st = (errno == 0)
            yield (s, st)

def read_repo_rel():
    import mip
    import time
    try:
        mip.install("github:mc0110/inetbox2mqtt/src/release.py", target = "/")
    except:
        import machine
        machine.reset()
    time.sleep(1)    
    import release
    q = release.rel_no
    print("Repo relase-no: " + q)
    return q

