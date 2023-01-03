# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# 
from machine import soft_reset, reset
from gen_html import Gen_Html
from nanoweb import HttpError, Nanoweb, send_file
import uasyncio as asyncio
import gc


def init(w):
    global gh
    global reboot
    global soft_reboot
    global repo_update
    gc.enable()
    gh = Gen_Html(w)
    reboot = False
    soft_reboot = False
    repo_update = False


async def command_loop():
    global reboot
    global soft_reboot
    global repo_update
    global repo_update_comment
    while True:
        await asyncio.sleep(0.5) # Update every 10sec
        if reboot:
            await asyncio.sleep(10) # Update every 10sec
            reset()
        if soft_reboot:
            await asyncio.sleep(10) # Update every 10sec
            soft_reset()
        if repo_update:
            import cred
            rel_new = cred.read_rel()
            repo_update_comment = ""
            if (rel_new != gh.wifi.rel_no):
                for i, st in cred.update_repo():
                    print(i, st)
                    if st:
                        repo_update_comment = i + " loaded"
                    else:
                        repo_update_comment = i + " not successful"    
                await asyncio.sleep(2) # sleep for 500ms
                gh.refresh_connect_state()
            else:    
                repo_update_comment = "repo up to date"
                await asyncio.sleep(5) # sleep
            repo_update = False
        gh.wifi.set_led(2)
        

# Declare route directly with decorator
#@naw.route('/')
async def index(r):
    global gh
    global repo_update
    repo_update = False
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleRoot())

#@naw.route('/loop')    
async def loop(r):
    global repo_update_comment
    global repo_update
    
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if repo_update:
        await r.write(gh.handleMessage("Update is running -> " + repo_update_comment, "/", "Back",("3","/loop")))
    else:    
        await r.write(gh.handleMessage("Update finalized", "/", "Back",("5","/")))
        
    
#@naw.route('/ta')    
async def toggle_ap(r):
    global gh
    if not(gh.wifi.set_sta()):
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r