# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
import time
import lib.connect as connect
appname = "inetbox2mqtt"

#sleep to give some boards time to initialize, for example Rpi Pico W
time.sleep(3)

w=connect.Wifi()
w.set_appname(appname)
w.set_sta(1)

w.run_mode(2)

if w.run_mode() > 1:
    
    print("Update-Process startetd")
    import cred
    cred.set_cred_json()
    for i in cred.update_repo():
        print(i)
    w.run_mode(w.run_mode() - 2)     
    machine.reset()
    
    
else:
    if w.creds() and w.set_sta() and (w.run_mode() == 1):
        print("Normal mode activated - for chance to OS-mode type in terminal:")
        print(">>>import os")
        print(">>>os.remove('run_mode.dat'")    
        import truma_serv
        truma_serv.run(w)
    else:
        print("OS mode activated")
        import web_os_run
        web_os_run.run(w)
    
