# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# This snippet should you include in your software project to use the wifi manager 

import logging
import web_os as os
from nanoweb import Nanoweb
import uasyncio as asyncio
from machine import UART, Pin
from lin import Lin



log = logging.getLogger(__name__)
connect = None


# major ctrl loop for inetbox-communication
async def lin_loop():
    global lin
    await asyncio.sleep(1) # Delay at begin
    log.info("lin-loop is running")
    while True:
        lin.loop_serial()
        if not(lin.stop_async):
            await asyncio.sleep_ms(1)

async def mqtt_loop():
    global connect
    log.info(f"mqtt_loop:")
    connect.set_mqtt(1)
    log.info(f"await loop_mqtt")
    await connect.loop_mqtt()

        
def run(w, lin_debug, inet_debug, webos_debug, naw_debug, logfile):
    global lin
    global connect
    connect = w
    if naw_debug:
        log.setLevel(logging.DEBUG)
        naw = Nanoweb(80, debug = True)
    else:    
        log.setLevel(logging.INFO)
        naw = Nanoweb(80)

    # connect.set_proc(subscript = connect.callback, connect = connect.conn_callback)
        
    log.info(f"run lin:{lin_debug} inet:{inet_debug} webos:{webos_debug} naw:{naw_debug} file:{logfile}")
    # debug=True for debugging
    
    # hw-specific configuration
    log.info(f"run uart:{w.p.get_data('lin_uart')} tx:{w.p.get_data('lin_tx')} rx:{w.p.get_data('lin_rx')}")
    log.info(f"HW-Check {w.platform_name}")
    if (w.platform=="rp2"):
        serial = UART(w.p.get_data("lin_uart"), baudrate=9600, bits=8, parity=None, stop=1, timeout=3, rx=Pin(w.p.get_data("lin_rx")), tx=Pin(w.p.get_data("lin_tx"))) # this is the HW-UART-no 2
    if (w.platform=="esp32"):
        serial = UART(w.p.get_data("lin_uart"), baudrate=9600, bits=8, parity=None, stop=1, timeout=3, rx=w.p.get_data("lin_rx"), tx=w.p.get_data("lin_tx")) # this is the HW-UART-no 2    
            
    # Initialize the lin-object
    lin = Lin(serial, w.p, lin_debug, inet_debug)
    os.init(w, lin, naw, webos_debug, logfile)

    naw.STATIC_DIR = "/"
    
    loop = asyncio.get_event_loop()
    log.info("Start nanoweb server")
    loop.create_task(naw.run())
    loop.create_task(lin_loop())
#    loop.create_task(mqtt_loop())
    log.info("Start OS command loop")
    loop.create_task(os.command_loop())
    loop.run_forever()        
