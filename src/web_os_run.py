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

# debug=True for debugging

def run(w):
    naw = Nanoweb(80)
    os.init(w)

    naw.STATIC_DIR = "/"
    naw.routes = {
         '/': os.index,
         '/ta': os.toggle_ap,
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
         '/rb': os.reboot,
         '/upload/*': os.upload,
         '/fm*': os.fm,
         '/dir*': os.set_dir,
     }


    loop = asyncio.get_event_loop()
    loop.create_task(naw.run())
    loop.run_forever()        

