# MIT License
# 
# Copyright (c) 2022  Dr. Magnus Christ (mc0110)
#
#
# version 0.8.2
#
# this project is based on the LIN Specification Package Revision 2.2A
#
# The essential basis is to incorporate the results of the specification in such a way that 
# there are no performance problems. Therefore, for example, RAW PIDs are processed in which 
# the parity bits have not been separated. These are shown on pages 53ff of the specification. 
# Thus 3C/3D with parity becomes 3C/7D. If this leads to confusion, I apologise.
# Same approach for the raw PID 0xD8. This corresponds to a PID 0x18
# This module has been optimised for high performance.  

from tools import calculate_checksum, PIN_MAP
import inetboxapp
import logging
import uasyncio as asyncio


class Lin:

    ts_response_buffer = []
    cpp_in_buffer = [bytes([]),bytes([]),bytes([]),bytes([]),bytes([]),bytes([])]
    updates_to_send = False
    update_request = False
    cpp_buffer = {}
    cmd_buf = {}
    cnt_rows = 1
    stop_async = False
    log = logging.getLogger(__name__)
    cnt_in = 0
# Same approach for the raw PID 0xD8. This corresponds to a PID 0x18
    d8_alive = False


    # Only for display control / slow event timing
    CNT_ROWS_MAX = 200
    
    # Check Alive-status periodically - with 1ms delay it is appx. 9s
    # there must be more than 1 D8-requests in this periode, than is alive status "ON"
    # otherwise it would set "OFF" 
    CNT_IN_MAX = 9000
    
    DISPLAY_STATUS_PIDS = [bytes([0x20]), bytes([0x61]), bytes([0xE2])]
    
    
    # the correct (full) preamble starts in the first frame, but we see only one type of
    # frames, all with the same length - so we can use a frame-preamble with a shorter length,
    # starting in the 2. frame
    BUFFER_PREAMBLE = bytes([0x00, 0x00, 0x22, 0xFF, 0xFF, 0xFF, 0x54, 0x01])


    BUFFER_HEADER_RECV  = bytes([0x14, 0x33])
    BUFFER_HEADER_TIMER = bytes([0x18, 0x3D])
    BUFFER_HEADER_02    = bytes([0x02, 0x0D])
    BUFFER_HEADER_03    = bytes([0x0A, 0x15])
    BUFFER_HEADER_WRITE = bytes([0x0C, 0x32])


    def __init__(self, serial, pin_map, lin_debug, inet_debug):
        self.loop_state = False
        self.serial = serial
        self.pin_map = pin_map
        self.cnt_rows = 1
        if lin_debug:
            self.log.setLevel(logging.DEBUG)
        self.lin_debug = lin_debug    
        self.app = inetboxapp.InetboxApp(inet_debug)
        self.pin_map.set_led("lin_led", False)
        print("Lin initialized")

    def response_waiting(self):
        return len(self.ts_response_buffer)


    def _send_answer_str(self, data_str):
        self._send_answer(self, serial, bytes.fromhex(data_str.replace(" ","")))


    def _send_answer_w_cs_calc(self, databytes, pid_for_checksum=None):
        if not pid_for_checksum:
            cs = calculate_checksum(databytes)
        else:
            cs = calculate_checksum(bytes([pid_for_checksum]) + databytes)
        self.send_answer(self, serial, databytes.extend([cs]))    


    def _send_answer(self, databytes):
        self.serial.write(databytes)
        self.serial.flush()
        self.log.debug("out > " + str(databytes.hex(" ")))
        self.pin_map.toggle_led("lin_led")


    def prepare_tl_str_response(self, message_str, info_str):
        self.prepare_tl_response(bytes.fromhex(message_str.replace(" ","")))
        if info_str.startswith("_"):
            self.log.debug(info_str)
        else:    
            self.log.info(info_str)


    def prepare_tl_response(self, messages):
        self.ts_response_buffer.extend([messages])


    def _answer_tl_request(self):
        if len(self.ts_response_buffer):
            databytes = bytes(self.ts_response_buffer[0])
            self.ts_response_buffer.pop(0)
            self._send_answer(databytes)
        else:
            self.log.debug("unexpacted behavior - nothing to send")


    def no_answer(self, s, p):
        if self.stop_async:
            self.stop_async = self.response_waiting()
        self.updates_to_send = (self.app.upload_buffer or self.app.upload02_buffer)
        if p.startswith("_"): return
        self.log.debug(p)

       
    def display_status(self):
        pass
#        if self.info:
#            print()
#            print("Overview received buffers")
#            for key in self.cpp_buffer.keys():
#                 print(f"Buf[{key}]={self.cpp_buffer[key]}")
#            print("-----------------------------")
#            print()


    def assemble_cpp_buffer(self):
        # gather the transfered frames 
        # preamble "00 1E 00 00 0x22 0xFF 0xFF 0x54 0x01"
        # buffer id (2 bytes)
        buf = bytes([])
        for i in range(5):
            buf += self.cpp_in_buffer[i]
        #print(buf.hex("+"))    
        if buf[:8] != self.BUFFER_PREAMBLE:
            self.log.debug("buffer preamble doesn't match")
            return False
        buf_id = buf[8:10]
        self.d8_alive = True
        self.cpp_buffer[buf_id] = buf[10:]
        self.log.debug(f"Buf[{buf_id}]={self.cpp_buffer[buf_id]}")
        self.app.process_status_buffer_update(buf_id, self.cpp_buffer[buf_id])
        return True


    # send out - warm water
    def generate_inet_upload(self, s, p):
        # Message warm water / counter = 1
#         self.prepare_tl_response(bytes.fromhex("03 10 29 fa 00 1f 00 1e 8b".replace(" ","")))
#         self.prepare_tl_response(bytes.fromhex("03 21 00 00 22 ff ff ff b9".replace(" ","")))
#         self.prepare_tl_response(bytes.fromhex("03 22 54 01 0c 32 02 22 23".replace(" ","")))
#         self.prepare_tl_response(bytes.fromhex("03 23 00 00 00 00 00 00 d9".replace(" ","")))
#         self.prepare_tl_response(bytes.fromhex("03 24 3a 0c 00 00 01 01 90".replace(" ","")))
#         self.prepare_tl_response(bytes.fromhex("03 25 00 00 00 00 00 00 d7".replace(" ","")))
#         self.prepare_tl_response(bytes.fromhex("03 26 00 00 00 00 00 00 d6".replace(" ","")))

        if self.app.upload_buffer:
            self.log.debug("heater_status to be generated")
            self.cmd_buf = self.app._get_status_buffer_for_writing()
            self.stop_async = True
            if self.app.upload_buffer > 0: self.app.upload_buffer -= 1

        if self.app.upload02_buffer:
            self.log.debug("aircon_status to be generated")
            self.cmd_buf = self.app._get_status_buffer1_for_writing()
            self.stop_async = True
            if self.app.upload02_buffer > 0: self.app.upload02_buffer -= 1

        if (self.cmd_buf == None) or (self.cmd_buf == {}):
            self.log.debug("cmd_buffer is empty")
            return
        self.d8_alive = True
        self.stop_async = True
        for i in self.cmd_buf:
            self.prepare_tl_response(i)
        self.updates_to_send = False
        if p.startswith("_"): return
        self.log.debug(p)

    async def watchdog(self):
        self.log.info("watchdog activated")
        await asyncio.sleep(60)
        if (self.app.status["alive"][0] == "ON"):
            self.log.info("watchdog deactivated_s1")
            return
        await asyncio.sleep(60)
        if (self.app.status["alive"][0] == "ON"):
            self.log.info("watchdog deactivated_s2")
            return
        await asyncio.sleep(60)
        if (self.app.status["alive"][0] == "ON"):
            self.log.info("watchdog deactivated_s3")
        else:
            if self.lin_debug:
                self.log.debug("system reboot in debug_mode suppressed")
            else:    
                self.log.info("system reboot required")
                import machine
                machine.reset()
    
    # check alive status
    def status_monitor(self):
        self.cnt_in += 1
        if not(self.cnt_in % self.CNT_IN_MAX):
            self.cnt_in=0
            self.app.status["alive"] = ["ON", True, False] 
# Same approach for the raw PID 0xD8. This corresponds to a PID 0x18
            if self.d8_alive:
                self.app.status["alive"][0] = "ON"
            else:    
                self.app.status["alive"][0] = "OFF"
            self.d8_alive = False
            self.pin_map.set_led("lin_led", False)



    async def loop_serial(self):

        self.status_monitor()        
        # New input process: idea is, nothing to forget. So there is a turing-machine nessecary. This read 1 byte and decide to switch in the next level or to throw the input away
        # So there is a much higher probability for synchronizing
        if not(self.serial.any()):
            return
        self.pin_map.dtoggle_led("lin_led")
        ####### Many thanks to florent314 see also issue #69
        #line = self.serial.read()
        ##if self.loop_state: # this means level 2
        ##    if line[0] == 0x55: # here it is clear, we saw a correct synchronizing
        ##        line = bytes([0x00, 0x55]) + self.serial.read(1)
        ##        self.loop_state = False
        ##        # this is the exit point of the turing machine
        ##    else: # recycling the byte, if it is 0x00 
        ##        self.loop_state = (line[0] == 0x00) # e.g. 0x00 0x00 0x55 would be found
        ##        return
        ##else: # this is level 1 - waiting for 0x00 for next level
        ##    self.loop_state = (line[0] == 0x00)
        ##    if not(self.loop_state):
        ##        #if self.debug:
        ##       print(f"in < {line[0]:02x} not a proper sync -wait for sync-")
        ##        pass
        ##    return
        line = b'\x00'+ self.serial.read(1)
        while(not line[1]==0x55 ):
            if self.serial.any()==0:
                return
            line = b'\x00'+ self.serial.read(1)
            
        line += self.serial.read(1)
        #line = self.serial.read(2)

        #if(not len(line)==11 ):
        #    
        #    return

        raw_pid = line[2]
        if raw_pid in self.DISPLAY_STATUS_PIDS: print(f"status-message found with {raw_pid:x}")#0x20 0x61 0xe2 

# Same approach for the raw PID 0xD8. This corresponds to a PID 0x18
        if raw_pid == 0xd8:
            self.d8_alive = True
            self.app.status["alive"] = ["ON", True, False] 
            self.pin_map.set_led("lin_led", True)
            self.log.debug(f"in < {line.hex(" ")}")
            s = False
            if not(self.app.upload_wait): s = (self.app.upload_buffer or self.app.upload02_buffer)
            if s:
                self.app.upload_wait = 4
                self.stop_async = True
                self.log.debug("0x18 - update-requested")
                self._send_answer(bytearray.fromhex("ff ff ff ff ff ff ff ff 27".replace(" ","")))
                return
            else:
                self._send_answer(bytearray.fromhex("fe ff ff ff ff ff ff ff 28".replace(" ","")))
                if self.app.upload_wait:
                    self.app.upload_wait -= 1
                return
# send requested answer to 0x3d -> 0x7d with parity) but only, if I have the need to answer
        if raw_pid == 0x7d:
            if self.response_waiting():
                self.log.debug(f"in < {line.hex(" ")}")        
                self._answer_tl_request()
                return
            else: return
              
        while self.serial.any()<9:
            pass
        #print("Debug:ici")
        line += self.serial.read(9)
        deb=""
        for b in line:
            deb=deb+f"{b:02x} "
        if(len(line)>2):
            print("debug:%s, %d, 0x%x"%(deb,len(line),line[2]))
        else:
            print("debug:%s, %d"%(deb,len(line)))
        # the idea is to trigger events from the loop-timing
        # seeing completed rows at this point (rows means LIN-frames)
        # but we don't use this functionality at the moment
        self.cnt_rows += 1
        self.cnt_rows = self.cnt_rows % self.CNT_ROWS_MAX
        if not(self.cnt_rows): self.display_status()
        
        self.log.debug(f"in < {line.hex(" ")}")
#        if len(line) != 12:
#            return              # exit, length isn't correct
#

# most of the following comments are only used in the test-phase
# so the idea was, to hide all comments with a begining underline


# multi-frame receive for buffer download from CPplus
        buf_trans_id = bytes([0x00, 0x55, 0x3c, 0x03])
        if (line[:4]==buf_trans_id) and (line[4] in range(0x21, 0x27)):
#            self.("Buffer-check:" + str(line.hex("-")))
            self.cpp_in_buffer[line[4] - 0x21] = line[5:-1] # fill into buffer-segment
#            self.log.debug(str(self.cpp_in_buffer[line[4] - 0x21].hex("*"))+ str(line[4] - 0x21))
            if (line[4] == 0x26):
                if (self.assemble_cpp_buffer()):
                    self.prepare_tl_str_response("03 01 fb ff ff ff ff ff 00", "_send ackn-response for buffer delivery") # ackn buffer-upload
                return # Line is stored in buffer - nothing else to do
            else:
                return

        cmd = line.hex(" ")
# single frame messages - answers to send buffer
# comments could be set "unshow" in info-log with a starting underline
# attention: this are raw frames with checksum -> see specification for details
        cmd_ctrl = {
            "00 55 3c 7f 06 b2 00 17 46 00 1f 4b": [self.prepare_tl_str_response, "03 06 f2 17 46 00 1f 00 87", "_B2 - response request"],  # B2-Message I - Initialization started
            "00 55 03 aa 0a ff ff ff ff ff ff 48": [self.no_answer, "", "_NAD 03 response - ack"],               # reaction to B2 - ackn
            "00 55 3c 03 06 b2 20 17 46 00 1f a7": [self.prepare_tl_str_response, "03 06 f2 17 46 00 1f 00 87", "B2 - identifier for NAD 03"],  # B2-Message II: Looking for my ID-no 17 46 00 1f
            "00 55 3c 03 06 b2 22 17 46 00 1f a5": [self.prepare_tl_str_response, "03 06 f2 17 46 00 1f 00 87", "B2 - initializer for NAD 03   -----------------> start registration"],  # B2-Message Initializer		
            "00 55 3c 7f 06 b0 17 46 00 1f 03 4a": [self.prepare_tl_str_response, "03 01 f0 ff ff ff ff ff 0b", "B0 - init finalized - send ackn ---------------> registration finalized"],  # B0-Message - registation finalized
            "00 55 3c 03 05 b9 00 1f 00 00 ff 1f": [self.prepare_tl_str_response, "03 02 f9 00 ff ff ff ff 01", "_Heartbeat for NAD 03 - send response"],  # Heartbeat
            "00 55 3c 03 10 29 bb 00 1f 00 1e ca": [self.no_answer, "", "_Frame 1 of buffer-transfer (6 frames) from CPplus"], #0xBB notice to send buffer
            "00 55 3c 03 10 0b ba 00 1f 00 1e e9": [self.generate_inet_upload, "", "BA-request: upload started"], # 0xBA request for inetBox to upload the buffer-frames
            "00 55 03 aa 0a ff ff ff ff ff ff 48": [self.no_answer, "", "_ackn from CPplus"], # ackn from CPplus
            }
        if not(cmd in cmd_ctrl.keys()):
            #self.log.debug(str(line.hex(" ")) + "-> no processing")
            return # no processing necessary
        cmd_ctrl[cmd][0](cmd_ctrl[cmd][1], cmd_ctrl[cmd][2]) # do it
        return 
