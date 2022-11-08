# inetbox2mqtt
# microPython inetbox2mqtt
**communicate over MQTT protocol to simulate a TRUMA INETBOX**

## Acknowledgement
The software is a derivative of the github project [INETBOX](https://github.com/danielfett/inetbox.py) by Daniel Fett. 
Thanks to him, as well as the preliminary work of [WoMoLIN](https://github.com/muccc/WomoLIN), these cool projects have become possible.

This project here was developed and tested for an ESP32 (first generation) with 4 MB memory. The software also works on other ESP32 models and probably, with small adjustments (UART address, pins), also on other hardware. First tests on a Raspberry Pi 2 and Pico W were successful, too. However, the source code for these has not yet been published.

## Disclaimer
My solution for the ESP32 has so far only been tested with my own TRUMA/CPplus version. The LIN module for the ESP32 works logically a bit different than Daniel's software, because I had performance problems with a 1:1 port for the ESP32. On the other hand, the module in the current version for the ESP32 has proven to be very stable and CPplus-compatible. **Nevertheless, it should be mentioned here that I do not assume any liability or guarantee for its use.**

## Electrics
For the wiring of the LIN bus via the TJA1020 to the UART, please refer to the project [INETBOX](https://github.com/danielfett/inetbox.py) mentioned above. On the ESP32, I use the UART2 (**Tx - GPIO17, Rx - GPIO16**):

![1](https://user-images.githubusercontent.com/65889763/200187420-7c787a62-4b06-4b8d-a50c-1ccb71626118.png)

These are to be connected to the TJA1020. No level shift is needed (thanks to the internal construction of the TJA1020). It also works on 3.3 V levels, even if the TJA1020 is operated at 5 V. 

## MQTT topics - almost the same, but not exactly the same
The MQTT commands ***(set-topics)*** are identical to Daniel's command usage [INETBOX](https://github.com/danielfett/inetbox.py). 

We will try to keep the topics and payloads as equal as possible. However, the published topics look a little different. The ESP32 only sends selected topics and omits all the timers, checksum, command_counter, etc. (all self-explanatory). If there is a need for adaptation, I am at your disposal. The timing for the sending of the topic has also been modified, i.e. the ESP32 only sends a topic if something has changed for the individual topic. This is different with Daniel's program, which always writes the whole status register. With my program, there is an alive topic, which shows the status of the connection to the MQTT broker and to the CPplus (see also ESP32 LEDs).

## ESP32 LEDs
Since the ESP32 has so many GPIOs, I programmed two LEDs. The LEDs are to be connected in negative logic:

            GPIO-pin ----- 300-600 Ohm resistor ----- LED ----- +3.3V

GPIO12 indicates when the MQTT connection is up. GPIO14 indicates when the connection to the CPplus is established. 

## Alive topic
Short digression: The CPplus only sends 0x18 (with parity it is 0xD8) requests if an INETBOX is registered. This can be recognised by the third entry in the index menu on the CPplus, among other things. The ESP32 answers these requests. Only when it receives 0x18 messages, the connection to the CPplus is established and the registration has taken place. This makes it easy to find out if there is an electrical problem. If the LED (GPIO14, see ESP32 LEDs) is lit, communication with the CPplus is established. The ESP32 also outputs this as an "alive" topic via the MQTT connection (approx. every 60 sec): connection OK => payload: ON; connection not OK => payload: OFF.

## Good news for Home Assistant users
To make it even easier to set up the INETBOX simulator together with the [Home Assistant](https://www.home-assistant.io/) smarthome system, the [auto-discovery function of home assistant](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) is implemented.

After the ESP32 has connected to the MQTT broker, it sends the installation codes. If the Home Assistant server is also connected to the MQTT broker, the entities are all generated automatically. They all begin with 'truma_'. Since they are not persistent, this automatic generation also takes place when the Home Assistant server is restarted.

The Home Assistant's own MQTT broker, which is available as an add-on, can also be used. If you use other smart home systems, you can simply ignore the messages. In the [docs](https://github.com/mc0110/inetbox2mqtt/tree/main/doc), there is an example of a frontend solution in Home Assistant.

## Alive topic
Short digression: The CPplus only sends 0x18 (with parity it is 0xD8) requests if an INETBOX is registered. This can be recognised by the third entry in the index menu on the CPplus, among other things. The ESP32 answers these requests. Only when it receives 0x18 messages, the connection to the CPplus is established and the registration has taken place. This makes it easy to find out if there is an electrical problem. If the LED (GPIO14, see ESP32 LEDs) is lit, communication with the CPplus is established. The ESP32 also outputs this as an "alive" topic via the MQTT connection (approx. every 60 sec): connection OK => payload: ON; connection not OK => payload: OFF.

## MicroPython
After the first tests, I was amazed af how good and powerful the [microPython.org](https://docs.micropython.org/en/latest/) platform is. However, the software did not run with a kernel from July (among other things, the bytearray.hex was not implemented there yet). Now is is ok.

The micropython MQTT packages are currently still experimental and cannot yet establish MQTT TLS connections. Thanks a lot to Thorsten [tve/mqboard](https://github.com/tve/mqboard) for his work.

## Installation instructions
### Alternative 1: With esptool
The .bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:

    esptool.py write_flash 0 flash_dump_esp32_lin_v08_4M.bin

This is not a partition but the full image for the ESP32 and only works with the 4MB chips. The address 0 is not a typo.

After flashing, please reboot the ESP32 and connect it to a serial terminal (e.g. miniterm, putty, serialport) (baud rate: 115700) fur further steps like checking if everything is working ok.

### Alternative 2: With a microPython IDE
Handling the *.py files and adapting and testing them is much easier if you use a microPython IDE. I can recommend the [Thonny IDE](https://thonny.org/), which is available on various platforms (Windows, macOS, Linux) and can also handle different hardware (e.g. ESP8266, ESP32, Raspberry Pi 2).

To do this, you first have to install an up to date microPython version, to be found at [micropython/download](https://micropython.org/download/). My tests were done with upython-version 19.1-608.

Then all .py files (including the lib sub-directory) must be loaded onto the ESP32 via the IDE.

### Execution
If you put all files into the root directory of the ESP32 - either as complete .bin file with the esptool, or as .py files with a microPython IDE - the ESP32 will start the program after a reboot. You can abort a program in the IDE with CTRL-C. Since the files are set up in such a way that the program starts directly after booting, the program must first be interrupted. This is done with CTRL-C.

After that, you have full control with Thonny or another microPyhton IDE and can change, save, and execute the .py files.

### Credentials
On first run of the program, the ESP32 will ask for the credentials for the MQTT broker (IP, Wifi SSID and password, username and password). These are then written in plain text to a file *credentials.py* on the ESP32.

The entries are then displayed again for confirmation, and the query is repeated until you have confirmed with ***yes***.

The process of providing the credentials for an initial setup does not have to be repeated, as long as the file *credentials.py* remains on the ESP32.
 
Alternatively, you can directly write (and edit) this file with a microPython IDE into the root directory of the ESP32. In this case, there is no query of the credentials, as the file *credentials.py* is already available on the ESP32.

For placing the files and creating the credentials on the ESP32, it does not need to be connected to the CPplus.

If everything is correctly set up and the ESP32 is rebooted, it should connect to the MQTT broker with a `connected` confirmation message.

Then you can establish the connection between the ESP32 and the LIN bus. This connection is not critical and can be disconnected at any time and then re-established. It should not be necessary to re-initialise the CPplus.
