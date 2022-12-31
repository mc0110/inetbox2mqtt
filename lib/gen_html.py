import os, machine
import lib.connect as connect
import gc

class Gen_Html():
    CR_M    = "    (c) Magnus Christ (2022) "

    CONNECT_STATE = ""

    HLP_TXT = {
            "root": '''This manager allows the administration of microPython devices via Wifi connection. The data of Wifi and MQTT broker can be stored in a credentials file even without internet access.
    Individual files can also be deleted or uploaded/downloaded. The data is stored encrypted on the device. 
    With an existing internet connection, software can be updated from GITHUB via OTA.

    ''',
            "files": 'Filemanager with full access to the ports filesystem. You see the sub-directories as links',
            "": 'No help description available',
        }
    # w-parameter is the connect-object    
    def __init__(self, w):
        self.wifi = w
        # generate the json-definition for credentials
        self.JSON = self.wifi.read_cred_json()
        # connection will be established
        self.wifi.connect()
        self.refresh_connect_state()
        self.reboot = False
        
    def refresh_connect_state(self):
        # collect state information
        # Wifi-class information
        self.CONNECT_STATE = self.wifi.get_state()
        gc.collect()
        # add mem state
        self.CONNECT_STATE["mem_free"] = str(gc.mem_free())
        # add cred-file, with existing
        if self.wifi.creds():
            json = {}
            # convert JSON to json_result = {key: value}
            for i in self.JSON.keys():        
                json[i] = "0"
            # take results from cred-file {key: value}    
            a = self.wifi.read_creds(json)
            for key, val in a.items():
                self.CONNECT_STATE["cred_" + key] = val
        

    def head(self, refresh=None):
        tmp = '''
            <!DOCTYPE html>
            <html lang='en'>
            
            <head>
                <meta charset='UTF-8'>
             '''
        if refresh != None:
            tmp += '<meta http-equiv="refresh" content="' + refresh[0] + '; url=' + refresh[1] + '">'
        tmp += '''       
                <meta name= viewport content='width=device-width, initial-scale=1.0,'>
                <meta Content-Type='application/x-www-form-urlencoded'>
                    <style type='text/css'>
                        .body_style {background-color: rgb(197, 209, 227); font-size:100%; margin-left: 10%;margin-right: 10%;}
                        .label_style {margin: 5px; font-size: 100%;}
                        .help {background-color: white;color: darkgray;width: 100%;margin-left: auto;margin-right: auto;padding: 2%;justify-content: left;font-size:80%;margin-bottom:3%;}
                        .status {background-color: rgb(4, 4, 78);color: rgb(228, 223, 223);width: 100%;margin-left: auto;margin-right: auto;padding: 2%;justify-content: left;font-size:80%;margin-bottom:3%;}
                        .status_title {font-size: 140%;padding-bottom: 1%;}
                        .message {display: flex; background-color:aliceblue; justify-content: center; font-size:120%; margin:5%; padding: 3%;}
                        .center {display: flex; justify-content: center; font-size:100%;}
                        .entry {font-size:12px; margin: 10px;}
                        .entry_s {margin: 5px; font-size: 10px;}
                        .button {height: 32px;%; width:45%; font-size:100%; background-color: rgb(206, 206, 225);margin-top: 1%;border-radius:10%;}
                        .button_s {height:21px; width:80px; font-size:90%; background-color: rgb(206, 206, 206); margin-top: 1%;}
                    </style>
            </head>
        '''
        return tmp

    def handleHeader(self, title = "", hlpkey = None, refresh = None):
        def str_keys(pre):
            s = pre.strip("_")+": "
            ap_k = []
            for key in self.CONNECT_STATE.keys():
                if key.startswith(pre):
                    ap_k.append(key)
            ap_k.sort()
            for key in ap_k:
                s += "&nbsp;(" + key[len(pre):] + " = " + str(self.CONNECT_STATE[key]) + ")&nbsp;"
            return s
        
        tmp = self.head(refresh)
        tmp += "<body class='body_style'><div class='center'>"
        tmp += "<h2>" + self.wifi.appname + " " + title + "</h2>"
        tmp += "</div>"
        if hlpkey != None:
            tmp += "<div class='help'>" + self.HLP_TXT.get(hlpkey) + "</div>"
        tmp += "<div class='status'><div class='status_title'>State-info:<br></div>"
        tmp += str_keys("ap_") + "<br>"
        tmp += str_keys("sta_") + "<br>"
        tmp += str_keys("cred_") + "<br>"
        tmp += str_keys("run_") + "<br>"
        tmp += str_keys("mem_") + "<br>"
        tmp += "</div>"
        return tmp;


    def handleFooter(self, link, name, script):
        tmp = ""
        tmp += "<div>"+self.handleGet(link,name)+"</div>"
        tmp += script
    #    tmp += "<script src='/jquery224.js'></script>"
    #    tmp += "<script src='/gh.js'></script>"
        tmp += '<br><div class="center">This&nbsp; <span>' + self.CONNECT_STATE["port"] + '</span>&nbsp;  is running on&nbsp; <span>' + self.CONNECT_STATE["python"] + '</span></div>'
        tmp += " </body></html>"
        #print(tmp)
        return tmp

    def handleGet(self, lnk, name):
        tmp = "<form class='center' action='" + lnk + "' method='GET'>"
        tmp += "<input name='ButtonName' type='submit' class='button' value='" + name + "'></form> \n"
        return tmp


    def handlePost(self, path, name, txt, val): 
      tmp = "<div>"
      tmp += "<form action='" + path + "' method='POST'>" + txt + "<input type='text' name='message' placeholder='" + name + "' required>"
      tmp += "<input type='submit' class='button' name= '" + val + "' value='"+ val + "'>"
      tmp += "</form>"
      tmp += "</div> \n"
      return tmp

    def handleMessage(self, message, blnk, bttn_name):
        # refresh-object with (time, url)
        tmp = self.handleHeader("Message", refresh = ("5", "/"))
        tmp += "<div class='message'>" + message + "</div>"
        tmp += self.handleFooter(blnk,bttn_name, "")
        return tmp
    
    def handleRedirect(self, blnk):
        message = ""
        bttn_name = ""
        tmp = self.handleHeader("Message", refresh = ("5", "/"))
        tmp += "<div class='message'>" + message + "</div>"
        tmp += self.handleFooter(blnk,bttn_name, sc)
        return tmp


    # Main Page
    def handleRoot(self, Comment):
        tmp = self.handleHeader()
        if self.wifi.set_ap():
            tmp += self.handleGet("/ta","Reset AccessPoint")
        else:    
            tmp += self.handleGet("/ta","Start AccessPoint")
        if self.wifi.set_sta():
            tmp += self.handleGet("/ts","Reset STA Connect")
        else:    
            tmp += self.handleGet("/ts","Start STA Connect")
        tmp += self.handleGet("/wc","Credentials")
        tmp += self.handleGet("/dir/__","Filemanager")
        tmp += self.handleGet("/ur","Update Repo") + "<p>"
        if self.wifi.run_mode():
            tmp += self.handleGet("/rm", "Normal Run")+"<p>"
        else:    
            tmp += self.handleGet("/rm", "OS-Run")+"<p>"
        tmp += self.handleGet("/rb","Reboot") + "<p> \n"
        tmp += self.handleFooter("/","Back", "")
        return tmp

    def handleFileAction(self, link, dir, fn):
        tmp = "<form action='" + link + dir + " 'method='GET'>"
        tmp += "<input name='dir' type='hidden' value='" + dir + "'>"
        tmp += "<input name='fn' type='hidden' value='" + fn + "'>"
        tmp += "<input name='button' type='submit' class='button_s' value='Download'>"
        tmp += "<input name='button' type='submit' class='button_s' value='Delete'>"
        tmp += "<label class='label_style'>" + fn + "</label>"
        tmp += "</form> \n"
        return tmp
    
    def handleUpload(self, dir):
        dir1 = dir
        if dir == "/":
            dir1 = "/__/"
        
        tmp = "File-Upload<br><div><form  id='form' action='/upload' method = 'POST'><input type='file' id='file' name='file'> <input type='submit' class='button_s' value='Upload'> </form>"
        tmp += " <script>async function upload(ev) { const file = document.getElementById('file').files[0]; if (!file) {return;}"
        tmp += "await fetch('/upload" + dir1 + "',"
        tmp += "{method: 'POST', credentials: 'include', body: file, headers: {'Content-Type': 'application/octet-stream', 'Content-Disposition': `attachment; filename=${file.name}`,},}).then(res => {console.log('Upload accepted');"
        tmp += "//alert('upload completed'); \n window.location.href = '/dir" + dir + "';}); ev.preventDefault();}"
        tmp += "document.getElementById('form').addEventListener('submit', upload); \n </script> </div> \n"
        return tmp

    def handleFiles(self, dir):  
        def gen_dir_href(i):
            tmp = ""
            tmp += "<a href ='/dir"
            tmp +=  dir + i
            tmp += "' <text>"
            tmp +=  "(" + i + ")"
            tmp += "</text></a> "
            tmp += "<br>"
            return tmp

        def gen_dir_back_href():
            tmp = ""
            a2 = 1
            a1 = 0
            while a2>0:
                a = a1
                a1 = a2 - 1
                a2 = dir.find("/",a2) + 1
            if a1 == 0:
                return ""
            i = dir[:a]
            if i == "":
                i = "/__"
            tmp += "<a href ='/dir"
            tmp +=  i
            tmp += "' <text class='label_style'>"
            tmp +=  "(..)"
            tmp += "</text></a> "
            tmp += "<br>"
            return tmp
        
        print("handleFiles dir=", dir)
        if dir[-1] != "/":
            dir = dir + "/"
        if dir[0] != "/":
            dir = "/" + dir
        f = open("fm.html","w")    
        f.write(self.handleHeader("Filemanager  '" + dir + "'", ""))
        f.write("<div><div>")
        f.write(gen_dir_back_href())
        s = os.ilistdir(dir)   # directories
        for i in s:
            if i[1] == 0x4000:
                f.write(gen_dir_href(i[0]))
        s = os.ilistdir(dir)   # files
        for i in s:
            if i[1] == 0x8000:
                f.write(self.handleFileAction("/fm", dir, i[0]))
        if dir == '/':
            dir = '/__/'
        f.write("</div></div>")
        f.write("<br><br>" + self.handleUpload(dir) + "<br><br>") 
        f.write(self.handleFooter("/","Back", ""))
        f.close()
        return "fm.html"


    def handleScan_Networks(self):
        tmp = self.handleHeader("Wifi-Networks", "");
        tmp += self.wifi.scan_html()  
        tmp += "<br>" + self.handleGet("/scan", "Rescan") + self.handleGet("/wc", "Back to Input")
        tmp += self.handleFooter("/","Back", "")
        return tmp


    def handleCredentials(self, json_form):
        tmp = self.handleHeader("Credentials", "");
        tmp += "<p>"+ self.handleGet("/scan","Scan Wifis") + "</p> \n"
        if self.wifi.creds():
            tmp +="<p>" + self.handleGet("/dc","Delete Credentials") + "\n"
            if self.wifi.creds_bak():
                tmp += self.handleGet("/sc","Swap Credentials")
        else:
            tmp += "<p> Credential-File doesn't exist </p><br> \n"
            if self.wifi.creds_bak():
                tmp += self.handleGet("/rc","Restore Credentials")
                
        
        tmp += "<p><form action='/cp' method='POST'> \n"

        # json-format: key,[type, entryname, order]
        entries = sorted(json_form.items(), key=lambda x:x[1][2])
        for e in entries:
            if e[1][0] == "checkbox":
                tmp += "<label for='" + e[0] + "'>" + e[1][1] + "</label> <input type='" + e[1][0] + "' name='" + e[0] +"' placeholder='" + e[0] + "' value='True'><br><br> \n"
            else:    
                tmp += "<label for='" + e[0] + "'>" + e[1][1] + "</label> <input type='" + e[1][0] + "' name='" + e[0] +"' placeholder='" + e[0] + "' value=''> <br><br> \n"
        tmp += "<input type='submit' class='button' name='SUBMIT' value='Store Creds'></form>"
        tmp += "</p>"    
        tmp += self.handleFooter("/","Back", "")
        return tmp


