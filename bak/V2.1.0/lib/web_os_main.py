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

        
def run(w, lin_debug, inet_debug, webos_debug, naw_debug, log_file):
    global lin
    if naw_debug:
        log.setLevel(logging.DEBUG)
        naw = Nanoweb(80, debug = True)
    else:    
        log.setLevel(logging.INFO)
        naw = Nanoweb(80)
        
    log.info("run")
    # debug=True for debugging
    # hw-specific configuration
    # if ("ESP32" in uos.uname().machine):
    if (w.platform == "esp32"):
        
        log.info("Found ESP32 Board, using UART2 for LIN on GPIO 16(rx), 17(tx)")
        # ESP32-specific hw-UART (#2)
        serial = UART(2, baudrate=9600, bits=8, parity=None, stop=1, timeout=3) # this is the HW-UART-no 2
    elif (w.platform == "rp2"):
        # RP2 pico w -specific hw-UART (#2)
        log.info("Found Raspberry Pico Board, using UART1 for LIN on GPIO 4(tx), 5(rx)")
        serial = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=3) # this is the HW-UART1 in RP2 pico w
    else:
        log.debug("No compatible Board found!")
        
    # Initialize the lin-object
    lin = Lin(serial, lin_debug, inet_debug)
    os.init(w, lin, naw, webos_debug, log_file)

    naw.STATIC_DIR = "/"


    loop = asyncio.get_event_loop()
    log.info("Start nanoweb server")
    loop.create_task(naw.run())
    loop.create_task(lin_loop())
    log.info("Start OS command loop")
    loop.create_task(os.command_loop())
    loop.run_forever()        

