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


log = logging.getLogger(__name__)

connect = None

        
def run(w, loglevel="info"):
    
    if loglevel == "debug":
        log.setLevel(logging.DEBUG)
        naw = Nanoweb(80, debug = True)
    else:    
        log.setLevel(logging.INFO)
        naw = Nanoweb(80)
        
    log.info("run")
    # debug=True for debugging
    os.init(w, naw, loglevel)

    naw.STATIC_DIR = "/"


    loop = asyncio.get_event_loop()
    log.info("Start nanoweb server")
    loop.create_task(naw.run())
    log.info("Start OS command loop")
    loop.create_task(os.command_loop())
    loop.run_forever()        

