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
rel_no = "1.5.9"


#sleep to give some boards time to initialize, for example Rpi Pico W
time.sleep(3)

w=connect.Wifi()
w.appname = appname
w.rel_no = rel_no
w.set_sta(1)

# run-mode > 1 means OTA-repo-checks
if (w.run_mode() > 1):
    # if run_mode > 1, then there should be credentials
    # rp2 needs sometimes more than 1 reboot for wifi-connection
    if not(w.set_sta()): machine.reset()
    import cred
    # download the release-no from repo
    rel_new = cred.read_repo_rel()
    if (rel_new != rel_no):
        print("Update-Process starts ....")
        status = True
        cred.set_cred_json()
        for i, st in cred.update_repo():
            print(i, st)
            status = status and st
        # if status = False, then process wasn't successful    
        if not(status):
            machine.reset()
        else:
            # Repo download was successful
            # run_mode must be reset to the original value 
            w.run_mode(w.run_mode() - 2)
            machine.reset()
    else:
        print("release is actual")
        w.run_mode(w.run_mode() - 2)
        machine.soft_reset()

# normal mode (run mode == 1) or OS run mode (run_mode == 0) execution    
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
    
