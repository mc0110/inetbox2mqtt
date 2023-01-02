# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# 
from machine import reset
from gen_html import Gen_Html
from nanoweb import HttpError, Nanoweb, send_file
import uasyncio as asyncio
import gc


def init(w):
    global gh
    gc.enable()
    gh = Gen_Html(w)


async def command_loop():
    global gh
    while True:
        await asyncio.sleep(0.5) # Update every 10sec
        if gh.reboot:
            await asyncio.sleep(10) # Update every 10sec
            reset()
        if gh.update:
            import cred
            for i in cred.update_repo():
                print(i)
                gh.update_comment = i
                await asyncio.sleep(2) # sleep for 500ms
            gh.refresh_connect_state()
#            await asyncio.sleep(20) # Update every 10sec
            gh.update = False
        gh.wifi.set_led(2)
        

# Declare route directly with decorator
#@naw.route('/')
async def index(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleRoot())

#@naw.route('/loop')    
async def loop(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if gh.update:
        await r.write(gh.handleMessage("Update is running -> " + gh.update_comment, "/", "Back",("3","/loop")))
    else:    
        await r.write(gh.handleMessage("Update finalized", "/", "Back",("5","/")))
        
    
#@naw.route('/ta')    
async def toggle_ap(r):
    global gh
    if not(gh.wifi.set_sta()):
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You couldn't release both (AP, STA), then you loose the connection to the port", "/", "Back",("2","/")))
    else:
        gh.wifi.set_ap(not(gh.wifi.set_ap()))
        gh.refresh_connect_state()
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleRoot())

#@naw.route('/ts1')
async def set_sta(r):
    global gh
    a = gh.wifi.set_sta(1)
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if a:
        await r.write(gh.handleMessage("STA-connection established successfull", "/", "Cancel",("5","/")))
    else:
        await r.write(gh.handleMessage("Couldn't establish a STA-connection", "/", "Cancel",("5","/")))

#@naw.route('/ts')
async def toggle_sta(r):
    global gh
    if not(gh.wifi.set_ap()):
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You couldn't release both (AP, STA), then you loose the connection to the port", "/", "Back",("5","/")))
    else:
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        if not(gh.wifi.set_sta()):
            await r.write(gh.handleMessage("Try to establish a STA-connection", "/", "Cancel",("5","/ts1")))
        else:    
            gh.wifi.set_sta(0)
            gh.refresh_connect_state()
            await r.write(gh.handleMessage("STA connection deactivated", "/", "Back",("5","/")))
#        await r.write(gh.handleRoot())
        
#@naw.route('/rm')
async def toggle_run_mode(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if not(gh.wifi.creds()):
        await r.write(gh.handleMessage("You couldn't switch run-mode without credentials", "/", "Back",("5","/")))
    else:    
        gh.wifi.run_mode(1 - gh.wifi.run_mode())
        gh.refresh_connect_state()
        await r.write(gh.handleRoot())

#@naw.route('/wc')
# Generate the credential form    
async def creds(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleCredentials(gh.JSON))

#@naw.route('/scan')
async def scan_networks(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleScan_Networks())

#@naw.route('/cp')
async def cp(r):
    global gh
    json = {}
    # convert JSON to json_result = {key: value}
    for i in gh.JSON.keys():        
        json[i] = "0"       
    for i in r.args.keys():
        if r.args[i]=="True":
            json[i] = "1"
        else:    
            json[i] = r.args[i]
    # print("Converted result: ", json)
    # store in credentials.dat in format <key:value>
    gh.wifi.store_creds(json)
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are written", "/", "Back",("5","/wc")))
#    await r.write(gh.handleRoot())


#@naw.route('/dc')
async def del_cred(r):
    global gh
    gh.wifi.delete_creds()
    print("Credentials moved to bak")
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are deleted", "/", "Back",("5","/wc")))
#    await r.write(gh.handleCredentials(gh.JSON))


#@naw.route('/sc')
async def swp_cred(r):
    global gh
    gh.wifi.swap_creds()
    print("Credentials swapped")
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are swapped", "/", "Back",("5","/wc")))
#    await r.write(gh.handleCredentials(gh.JSON))
    
#@naw.route('/rc')
async def res_cred(r):
    global gh
    gh.wifi.restore_creds()
    gh.refresh_connect_state()
    print("Credentials restored")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are restored", "/", "Back",("5","/")))
#    await r.write(gh.handleCredentials(gh.JSON))
    
#@naw.route('/rc')
async def ur(r):
    global gh
    if gh.wifi.set_sta():
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("For repo-update press 'UPDATE'", "/ur1", "UPDATE",("5","/")))
    else:
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You need a STA-internet-connection", "/", "Back",("5","/")))

#@naw.route('/rc')
async def ur1(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    print("Repo update initiated")
    gh.wifi.run_mode(2)
    await r.write(gh.handleMessage("Repo update initiated", "/", "Back",("5","/rb")))

#@naw.route('/rb')
async def reboot(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Device will be rebooted", "/", "Continue",("4","/")))
    gh.reboot = True


#@naw.route('/upload')
async def upload(r):
    global gh
    dir = r.url.strip("/upload/")
    if dir == "__":
        dir = "/"
    else:
        dir = "/" + dir.strip("/") + "/"    

    if r.method == "POST":
        # obtain the filename and size from request headers
        filename = r.headers['Content-Disposition'].split('filename=')[1].strip('"')
        size = int(r.headers['Content-Length'])
        # sanitize the filename
        # write the file to the files directory in 1K chunks
        with open(dir + filename, 'wb') as f:
            while size > 0:
                chunk = await r.read(min(size, 1024))
                f.write(chunk)
                size -= len(chunk)
            f.close()        
        print('Successfully saved file: ' + dir + filename)
        await r.write("HTTP/1.1 201 Upload \r\n" )
    else:
        rp = gh.handleFiles(dir)
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)

#@naw.route('/fm*')
async def fm(r):
    global gh
    filename = r.param["fn"]
    direct = r.param["dir"]

    if r.param["button"]=="Delete":
        print("delete file: " + direct+filename)
        try:
            os.remove(direct+filename)
        except OSError as e:
            raise HttpError(r, 500, "Internal error")
        rp = gh.handleFiles(direct)
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)
    elif r.param["button"]=="Download":
        print("download file: " + filename)
        await r.write("HTTP/1.1 200 OK\r\n") 
        await r.write("Content-Type: application/octet-stream\r\n")
        await r.write("Content-Disposition: attachment; filename=%s\r\n\r\n" % filename)
        await send_file(r, direct+filename)
        rp = gh.handleFiles(direct)
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)


#@naw.route('/dir*')
async def set_dir(r):
    global gh
    new_dir = r.url[5:]
    if new_dir.startswith("__"):
        rp = gh.handleFiles("/")
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)
    else:
        rp = gh.handleFiles(new_dir)
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)

