# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# This snippet should you include in your software project to use the wifi manager 


import lib.web_os as os
from nanoweb import Nanoweb
import uasyncio as asyncio

connect = None

        
def run(w):
    global connect
    # debug=True for debugging
    naw = Nanoweb(80) #, debug = True)
    connect = w
    os.init(connect, naw)

    naw.STATIC_DIR = "/"


    loop = asyncio.get_event_loop()
    loop.create_task(naw.run())
    loop.create_task(os.command_loop())
    loop.run_forever()        

