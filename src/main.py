# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
import time
import connect
import machine

appname = "inetbox2mqtt"
rel_no = "1.5.3"


#sleep to give some boards time to initialize, for example Rpi Pico W
time.sleep(3)

w=connect.Wifi()
w.appname = appname
w.rel_no = rel_no
w.set_sta(1)


if (w.run_mode() > 1) and (w.set_sta()):
    import cred
    rel_new = cred.read_rel()
    if (rel_new != rel_no):
        print("Update-Process startetd")
        status = True
        cred.set_cred_json()
        for i, st in cred.update_repo():
            print(i, st)
            status = status and st
        if not(status):
            machine.reset()
        else:
            w.run_mode(w.run_mode() - 2)
            machine.soft_reset()
    else:
        print("release is actual")
        w.run_mode(w.run_mode() - 2)

if w.creds() and w.set_sta() and (w.run_mode() == 1):
    print("Normal mode activated - for chance to OS-mode type in terminal:")
    