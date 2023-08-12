# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
#
import logging
import os
from machine import soft_reset, reset
from gen_html import Gen_Html
from nanoweb import HttpError, Nanoweb, send_file
import uasyncio as asyncio
import gc
import random


log = logging.getLogger(__name__)
naw = Nanoweb(100)
# client = MQTTClient(config)
test_mqtt = False

def init(w, l, n, debug=False, logfile=False):
    if debug:
        log.setLevel(logging.DEBUG)
    else:    
        log.setLevel(logging.INFO)
    log.info("init")
    log.debug(f"init debug:{debug} logf:{logfile} l:{l} n:{n}")
    global gh
    global reboot
    global soft_reboot
    global repo_update
    global repo_success
    global repo_update_comment
    global naw
    global file
    global lin
    file = logfile
    lin = l
    naw = n
    gc.enable()
    gh = Gen_Html(w, lin)
    reboot = False
    soft_reboot = False
    global connect
    connect = w

def unquote(s):
    s = s.replace("+"," ")
    if '%' not in s:
        return s
    s = s.split("%")
#    print(s)
    a = s[0].encode("utf-8")
    for i in s[1:]:
#        print(bytearray.fromhex(i[:2]))
#        print(i[2:],i[2:].encode("utf-8"))
        a = a + bytearray.fromhex(i[:2]) + i[2:].encode("utf-8")
    return a.decode("utf-8")    


async def command_loop():
    global reboot
    global soft_reboot
    global connect
    global file
    while True:
        if file:
            logging._stream.flush()
            log.debug("stream_flush")

#         logging._stream = open("test.log", "a")
        await asyncio.sleep(3) # Update every 10sec
        if soft_reboot:
            log.debug("soft_reboot")
            await asyncio.sleep(5) # Update every 10sec
            log.info("Soft reset chip")
            soft_reset()
        if reboot:
            log.debug("reboot")
            await asyncio.sleep(5) # Update every 10sec
            log.info("Reset chip")
            reset()

# Declare route directly with decorator
@naw.route('/')
async def index(r):
    global gh
    global repo_update
    gc.collect()
    repo_update = False
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await send_file(r, gh.handleRoot())
#    await r.write(gh.handleRoot())
    
@naw.route('/s')
async def status(r):
    global gh
    global repo_update
    gh.refresh_connect_state()
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await send_file(r, gh.handleStatus("Device status", "/", "Back",("30","/")))
#    await r.write(gh.handleStatus("Device status", "/", "Back",("30","/")))

@naw.route('/loop')    
async def loop(r):
    pass
   
@naw.route('/ta')    
async def toggle_ap(r):
    global gh
    if not(gh.connect.set_mqtt()):
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You couldn't release both (AP, STA), then you loose the connection to the port", "/", "Back",("2","/")))
    else:
        gh.connect.set_ap(not(gh.connect.set_ap()))
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleRoot())

# @naw.route('/ts1')
# async def set_mqtt(r):
#     await r.write("HTTP/1.1 200 OK\r\n\r\n")
#     global gh
# #     while test_mqtt:
# #    await asyncio.sleep(5)
#     if gh.connect.set_mqtt():
#         await r.write(gh.handleMessage("MQTT-connection established successfull", "/", "Cancel",("5","/")))
#     else:
#         await r.write(gh.handleMessage("Try again to establish a MQTT-connection", "/", "Cancel",("5","/ts1")))

@naw.route('/ts')
async def set_mqtt(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if not(gh.connect.creds()):
        await r.write(gh.handleMessage("Sorry, you need credentials", "/", "Back",("5","/")))
    else:
        s = str(random.randint(0,255))
        await connect.client.publish("service/truma/set/test", s, qos=1)
        log.info(f"mqtt: message sent to <service/truma/set/test> {s}")
        await r.write(gh.handleMessage(f"send 'service/truma/set/test'> {s}", "/", "Back",("5","/")))
        
        
@naw.route('/rm')
async def toggle_run_mode(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if not(gh.connect.creds()):
        await r.write(gh.handleMessage("You couldn't switch run-mode without credentials", "/", "Back",("5","/")))
    else:
        a = gh.connect.run_mode()
        if a < 2: a = 1 - a
        else: a=0    
        gh.connect.run_mode(a)
        await r.write(gh.handleMessage("RUN mode changed", "/", "Back",("5","/")))

@naw.route('/wc')
# Generate the credential form    
async def creds(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await send_file(r, gh.handleCredentials(gh.JSON))


@naw.route('/scan')
async def scan_networks(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    if gh.connect.set_mqtt():
        await r.write(gh.handleScan_Networks())
    else:    
        await r.write(gh.handleMessage("This needs STA-mode", "/", "Back",("5","/")))

@naw.route('/heat_on')
async def wheater_on(r):
    global gh
    global lin
    lin.app.set_status("target_temp_water", "200")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Send Message: Water heater -> BOOST", "/", "Back",("5","/")))

@naw.route('/heat_off')
async def wheater_off(r):
    global gh
    global lin
    lin.app.set_status("target_temp_water", "0")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Send Message: Water heater -> OFF", "/", "Back",("5","/")))


@naw.route('/cp')
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
            json[i] = unquote(r.args[i])
    gh.connect.store_creds(json)
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are written", "/", "Back",("5","/")))


@naw.route('/dc')
async def del_cred(r):
    global gh
    gh.connect.delete_creds()
    gh.connect.run_mode(0)
    log.debug("Credentials moved to bak")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are deleted", "/", "Back",("5","/wc")))


@naw.route('/sc')
async def swp_cred(r):
    global gh
    gh.connect.swap_creds()
    log.debug("Credentials swapped")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are swapped", "/", "Back",("5","/wc")))
    
@naw.route('/rc')
async def res_cred(r):
    global gh
    gh.connect.restore_creds()
    log.debug("Credentials restored")
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Credentials are restored", "/", "Back",("5","/")))
    
@naw.route('/ur')
async def ur(r):
    global gh
    if gh.connect.set_mqtt():
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("For repo-update press 'UPDATE'", "/ur1", "UPDATE",("5","/")))
    else:
        await r.write("HTTP/1.1 200 OK\r\n\r\n")
        await r.write(gh.handleMessage("You need a STA-internet-connection", "/", "Back",("5","/")))

@naw.route('/ur1')
async def ur1(r):
    global gh
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    log.debug("Set update mode")
    gh.connect.run_mode(2)
    global reboot
    reboot = True
    await r.write(gh.handleMessage("Repo update initiated, port is rebooting ..", "/", "Back",("5","/")))

@naw.route('/rb')
async def s_reboot(r):
    global soft_reboot
    soft_reboot = True
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Device will be soft rebooted", "/", "Continue",("4","/")))

@naw.route('/rb2')
async def h_reboot(r):
    global reboot
    reboot = True
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Device resetted", "/", "Continue",("4","/")))

@naw.route('/rb1')
async def h_reboot(r):
    await r.write("HTTP/1.1 200 OK\r\n\r\n")
    await r.write(gh.handleMessage("Device will be hard rebooted", "/rb2", "Continue to reboot",("4","/")))

@naw.route('/upload*')
async def upload(r):
    global gh
    dir = r.url[7:]
    print("upload-section: "+dir)
    if dir == "": dir = "/"
    if r.method == "POST":
        if "__" in dir:
            dir = "/"
        else:
            dir = "/" + dir.strip("/") + "/"    
        # obtain the filename and size from request headers
        filename = unquote(r.headers['Content-Disposition'].split('filename=')[1].strip('"'))
        size = int(r.headers['Content-Length'])
        print("dir: "+dir+"  fn: "+filename)
        # sanitize the filename
        # write the file to the files directory in 1K chunks
        with open(dir + filename, 'wb') as f:
            while size > 0:
                chunk = await r.read(min(size, 1024))
                f.write(chunk)
                size -= len(chunk)
            f.close()        
        log.info('Successfully saved file: ' + dir + filename)
        await r.write("HTTP/1.1 201 Upload \r\n" )
#        await send_file(r, gh.handleFiles(dir))
    else:
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, gh.handleFiles(dir))

@naw.route('/fm*')
async def fm(r):
    global gh
    filename = unquote(r.param["fn"])
    direct = unquote(r.param["dir"])

    if r.param["button"]=="Delete":
        log.info("delete file: " + direct+filename)
        try:
            os.remove(direct+filename)
        except OSError as e:
            raise HttpError(r, 500, "Internal error")
        rp = gh.handleFiles(direct)
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, rp)
    elif r.param["button"]=="Download":
        log.info("download file: " + filename)
        await r.write("HTTP/1.1 200 OK\r\n") 
        await r.write("Content-Type: application/octet-stream\r\n")
        await r.write("Content-Disposition: attachment; filename=%s\r\n\r\n" % filename)
        await send_file(r, direct+filename)


@naw.route('/dir*')
async def set_dir(r):
    global gh
    new_dir = r.url[5:]
    if new_dir.startswith("__"):
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, gh.handleFiles("/"))
    else:
        await r.write("HTTP/1.1 200 OK\r\n")
        await send_file(r, gh.handleFiles(new_dir))

