# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# 
from machine import reset
from time import sleep
from gen_html import Gen_Html
from nanoweb import HttpError, Nanoweb, send_file


gh = Gen_Html()

# Declare route directly with decorator
#@naw.route('/')
async def index(r):
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleRoot(""))
    if gh.reboot: reset()

#@naw.route('/ta')    
async def toggle_ap(r):
    if not(gh.wifi.set_sta()):
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You couldn't release both (AP, STA), then you loose the connection to the port", "/", "Back"))
    else:
        gh.wifi.set_ap(not(gh.wifi.set_ap()))
        gh.refresh_connect_state()
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleRoot(""))
    
#@naw.route('/ts')
async def toggle_sta(r):
    if not(gh.wifi.set_ap()):
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You couldn't release both (AP, STA), then you loose the connection to the port", "/", "Back"))
    else:    
        gh.wifi.set_sta(not(gh.wifi.set_sta()))
        gh.refresh_connect_state()
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleRoot(""))
        
async def toggle_run_mode(r):
        gh.wifi.run_mode(not(gh.wifi.run_mode()))
        gh.refresh_connect_state()
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleRoot(""))

async def creds(r):
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleCredentials(gh.JSON))

async def scan_networks(r):
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleScan_Networks())

async def cp(r):
    json = {}
    # convert JSON to json_result = {key: value}
    for i in gh.JSON.keys():        
        json[i] = "0"       
    for i in r.args.keys():
        if r.args[i]=="True":
            json[i] = "1"
        else:    
            json[i] = r.args[i]
    print("Converted result: ", json)
    # store in credentials.dat in format <key:value>
    gh.wifi.store_creds(json)
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleRoot(""))


async def del_cred(r):
    gh.wifi.delete_creds()
    print("Credentials moved to bak")
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleCredentials(gh.JSON))


async def swp_cred(r):
    gh.wifi.swap_creds()
    print("Credentials swapped")
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleCredentials(gh.JSON))
    
async def res_cred(r):
    gh.wifi.restore_creds()
    gh.refresh_connect_state()
    print("Credentials restored")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleCredentials(gh.JSON))
    
async def ur(r):
    if gh.wifi.set_sta():
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("Repo will be updated", "/ur1", "Continue"))
    else:
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You need a STA-internet-connection", "/", "Back"))

async def ur1(r):
    import cred
    cred.update_repo()    
    gh.refresh_connect_state()
    print("Repo is updated")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Repo is updated", "/", "Back"))

async def reboot(r):
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Device will be rebooted", "/", "Continue"))
    gh.reboot = True


async def upload(r):
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

async def fm(r):
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


async def set_dir(r):
    new_dir = r.url[5:]
    if new_dir.startswith("__"):
        rp = gh.handleFiles("/")
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)
    else:
        rp = gh.handleFiles(new_dir)
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)

