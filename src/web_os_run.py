# MIT License
#
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
# This is part of the wifimanager package
# 
# This snippet should you include in your software project to use the wifi manager 


import web_os as os
from nanoweb import Nanoweb
import uasyncio as asyncio

connect = None

        
def run(w):
    global connect
    # debug=True for debugging
    naw = Nanoweb(80) #, debug = True)
    connect = w
    os.init(connect)

    naw.STATIC_DIR = "/"
    naw.routes = {
         '/': os.index,
         '/s': os.status,
         '/loop': os.loop,
         '/ta': os.toggle_ap,
         '/ts1': os.set_sta,
         '/ts': os.toggle_sta,
         '/rm': os.toggle_run_mode,
         '/wc': os.creds,
         '/scan':os.scan_networks,
         '/cp': os.cp,
         '/ur': os.ur,
         '/ur1': os.ur1,
         '/dc': os.del_cred,
         '/sc': os.swp_cred,
         '/rc': os.res_cred,
         '/rb': os.s_reboot,
         '/rb1': os.h_reboot,
         '/upload/*': os.upload,
         '/fm*': os.fm,
         '/dir*': os.set_dir,
     }

    loop = asyncio.get_event_loop()
    loop.create_task(naw.run())
    loop.create_task(os.command_loop())
    loop.run_forever()        

