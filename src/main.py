# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
#
import logging
import time
import connect
import machine, os
from args import Args

UPDATE = "update.py"

appname = "inetbox2mqtt"
rel_no = "2.6.5"


#sleep to give some boards time to initialize, for example Rpi Pico W
time.sleep(3)

args = Args()

file = args.get_key("file")
if file != None:
    f = open(file, "a")
    logging.basicConfig(stream=f)
    
log = logging.getLogger(__name__)


log.setLevel(logging.INFO)

log.info(f"release no: {rel_no}")
w=connect.Connect(args.get_key("hw"), debuglog=args.check("connect=debug"))
w.appname = appname
w.rel_no = rel_no

# run-mode > 1 means OTA-repo-checks
if (w.run_mode() > 1):
    # if run_mode > 1, then there should be credentials
    # rp2 needs sometimes more than 1 reboot for wifi-connection
    if not(w.set_sta(1)):
        machine.reset()
    import mip
    import time
    try:
        mip.install("github:mc0110/inetbox2mqtt/src/" + UPDATE, target = "/")
    except:
        import machine
        machine.reset()            
    time.sleep(1)    
    import update
    # download the release-no from repo
    rel_new = update.read_repo_rel()
    if (rel_new != rel_no):
        log.info("Update-Process starts ....")
        status = True    
#        cred.set_cred_json()
        for i, st in update.update_repo():
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
        log.info("release is actual")
        w.run_mode(w.run_mode() - 2)
        machine.soft_reset()

# normal mode (run mode == 1) or OS run mode (run_mode == 0) execution    
else:
    if w.creds() and (w.run_mode() == 1):
        log.info("Normal mode activated - for chance to OS-mode type in terminal:")
        w.connect()
        print(">>>import os")
        print(">>>os.remove('run_mode.dat')")    
        import main1
        main1.run(w, args.check("lin=debug"), args.check("inet=debug"), args.check("mqtt=debug"), args.get_key("file")!=None)
    else:
        log.info("OS mode activated")
        w.set_ap(1)
        w.connect()
        
        import web_os_main
        web_os_main.run(w, args.check("lin=debug"), args.check("inet=debug"), args.check("webos=debug"), args.check("naw=debug"), args.get_key("file")!=None)
    
