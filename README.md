# inetbox2mqtt
# microPython inetbox2mqtt
**communicate over mqtt protocol to simulate a TRUMA INETBOX**

## acknowledgement
The software is a derivative of the github project [INETBOX](https://github.com/danielfett/inetbox.py) by Daniel Fett. 
It is thanks to him and his project as well as the preliminary work of [WoMoLIN](https://github.com/muccc/WomoLIN) that these cool projects have become possible.

This project was developed on an ESP32. The current sources are tested accordingly on an ESP32 (1st generation) with 4MB. However, microPython allows other ports to be used. First tests on an RP2 pico w were successful. However, these have not yet been published.

## disclaimer
My solution for the ESP32 has so far only been tested with my own TRUMA / CPplus version. The LIN module for the ESP32 works logically a bit different than Daniel's software, because I had performance problems with a 1-1 port on the ESP32. On the other hand, the module in the current version has proven to be very stable and CPplus-compatible. **Nevertheless, it should be mentioned here that I naturally do not assume any guarantee for its use.**

## electrics
Accordingly, for the wiring - connection of the LIN bus via the TJA1020 to the UART, please refer to the project [INETBOX](https://github.com/danielfett/inetbox.py) mentioned above. On the ESP32 I use the UART2 (tx - gpio17, rx - gpio16). These are therefore to be connected to the TJA1020. No level shift is needed (thanks to the internal construction of the TJA1020). It also works on 3.3V levels, even if the TJA1020 is operated with 5V. 

## microPython
After the first tests, I was amazed at how good and powerful the microPython platform is [see e.g. MicroPython.org](https://docs.micropython.org/en/latest/).

Despite this, or perhaps because of it, it's all very fast-moving. For example, (to my astonishment) the software did not run with a kernel from July (among other things, the bytearray.hex wasn't implemented there yet).
The micropython MQTT packages are currently still experimental. Thanks a lot to Thorsten [tve/mqboard](https://github.com/tve/mqboard) for his work. Therefore, the current software cannot establish MQTT-TLS connections.  

## mqtt topics - almost the same, but not exactly the same
The mqtt commands ***(set-topics)*** are identical to Daniel's command usage [INETBOX](https://github.com/danielfett/inetbox.py). 

We will try to keep the topics and payloads as equal as possible. However, the published topics look a little different. The ESP32 only sends selected Topics, I spare the MQTT broker all the timers, checksum, command_counter, etc. These are all self-explanatory. These are all self-explanatory. If there is a need for adaptation, I am at your disposal. The timing of the topic sends has also been modified somewhat. The ESP32 only sends the topics if something has changed there and that for each individual topic. This is different with Daniel, he always writes the whole status register. There is an alive topic, which shows the status of the 

## esp32 leds
There is another additional feature. Since the ESP32 has so many gpio's, I programmed two LEDs. The LEDs are to be connected in negative logic, so 

            gpio-pin ---- resistor ----- LED ----- +3.3V.

gpio12 indicates when the MQTT connection is up. gpio14 indicates when the connection to the CPplus is established. 

## alive-topic
Short digression: The CPplus only sends D8 requests if an INETBOX is registered. This can be recognised by the third entry in the index menu on the CPplus, among other things. The ESP32 answers these requests. Only when it receives D8 messages is the connection to the CPplus established and has the registration worked. This makes it easy to find out if there is an electrical problem. If the LED is lit, communication with the CPplus is established.
The ESP32 also outputs this as a "alive" topic via the MQTT connection. This occurs approx. every 60sec. Connection OK, payload: ON, connection not OK, payload: OFF

## good news for home assistant-user
To make it even easier to set up the inetbox simulator together with the [home-assistant](https://www.home-assistant.io/) smarthome system , the [auto-discovery function of home assistant](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) is implemented. 

After the chip has connected to the mqtt broker, it sends the installation codes. If the home-assistant server is also connected to the mqtt broker, the entities are all generated automatically. They all begin with 'truma_'. Since they are not persistent, this generation also takes place when the home-assistant server is restarted. 

Of course, the home assistant's own MQTT broker, which is available as an add-on, can also be used. If you use other smart home systems, you can simply ignore the messages.  

# installation instructions
## quick-Start
The bin file contains both the python and the py files!
This allows the whole project to be flashed onto the ESP32 in one go. Of course, esptool must be installed for this. In my case, the tool already finds the serial port of the ESP automatically. Otherwise, the port can of course be specified. The ESP must be in programming mode (gpio0 to ground at start-up). Command is:


    esptool.py write_flash 0 flash_dump_esp32_lin_v08_4M.bin*.

This isn't a partition, it is the full image of the ESP32. Therefore, it only works with the 4MB chips, the address 0 is not a typro.

After flashing, please reboot the chip and connect to a serial terminal (e.g. miniterm, putty, serialport) (baud rate: 115700). 

### credentials
The chip will then log on and ask for the credentials. These are then written to a file *credentials.py*

    from mqtt_async import config

    config.server   = ''
    config.ssid     = ''
    config.wifi_pw  = ''
    config.user     = ''
    config.password = ''


 and the process does not have to be repeated. 
 
 So only enter the Wifi SSID and password as well as the IP of the MQTT broker and username, PW. The entries are then displayed again and the query is repeated until you have confirmed it with ***yes***.

Alternatively, this file can of course be written directly into the directory. In this case, there is no query of the data.

For these first steps, the ESP32 does not need to be connected to the CPplus. If everything has worked, the ESP32 should then connect to the MQTT broker -> confirmation message: connected.

Then establish the connection to the LIN bus. This connection is not critical and can be disconnected at any time and then re-established. It should not be necessary to reinitialise the CPplus.


## full installation path
Of course, the software also works on other ESP32 models and probably with small adjustments (UART address, pins) also on other HW ports (e.g. rp2 pico w). 

To do this, you first have to install a Python version that is as new as possible. These can be found at [micropython/download](https://micropython.org/download/). My tests were done with upython-version 19.1-608.

Then all .py files (including the lib subdirectory) must be loaded onto the chip. The usual tools can be used for this. Please note that *credentials.py* (see above) must also be present.

### IDE 
Handling the *.py files and adapting and testing them is much easier if you use an microPython IDE. 

For this I can recommend the [Thonny IDE](https://thonny.org/). Even though there is a microPython extension for PyCharm, the result is far less suitable for everyday use than the Thonny IDE. The IDE is available on all platforms (Win, Mac, Linux) and can also handle different ports (ESP8266, ESP32, RP2).
But this is certainly a matter of taste and the choice of the appropriate IDE is up to everyone.

### execution
If you put all the files into the directory, the chip will start the programm after a reboot.
A programm abort works with Ctrl-C. Since the files are set up in such a way that the programm starts directly after booting, the programm must first be interrupted. This is done with ctrl-C. 

After that, you have full control with Thonny or another IDE and can change, save and execute the files.

