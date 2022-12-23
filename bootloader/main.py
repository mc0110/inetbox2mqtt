# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the inetbox2mqtt package
# 
# 
# After reboot the port starts with boot.py and main.py
#
# This code-segment needs to be named "main.py"
#
#
#
#
# Use this commands to connect to the network 
#
# import network
# s = network.WLAN(network.STA_IF)
# s.active(True)
# s.connect("<yourSSID>","<YourWifiPW>")
# print('network config:', s.ifconfig())
# mip.install("github:mc0110/inetbox2mqtt/source/bootloader/main.py","/")
# 
# import main
#
# The last command starts the download-process of the whole suite
# The download overwrites the main-program, so you see this process only once



import time, os
import mip
#sleep to give some boards time to initialize, for example Rpi Pico W
time.sleep(3)

# bootloader for the whole suite
tree = "github:mc0110/inetbox2mqtt/source"

env = [
    ["Kalman.py", "/"],
    ["boot.py", "/"],
    ["conversions.py", "/"],
    ["crypto_keys.py", "/"],
    ["duo_control.py", "/"],
    ["imu.py", "/"],
    ["inetboxapp.py", "/"],
    ["lin.py", "/"],
    ["main.py", "/"],
    ["set_credentials_encrypt.py", "/"],
    ["spiritlevel.py", "/"],
    ["tools.py", "/"],
    ["truma_serv.py", "/"],
    ["vector3d.py", "/"],
    ["logging.py", "/lib/"],
    ["mqtt_async.py", "/lib/"],
    ]

for i in range(len(env)):
    mip.install(tree+env[i][1]+env[i][0], target= env[i][1])


import set_credentials_encrypt
import truma_serv

