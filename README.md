<div align = center>

# inetbox2mqtt
## Control your TRUMA heater over a MQTT broker

### Version for ESP32 and RP pico w
<br/>

[![Badge License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt)
 &nbsp;
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)

</div>
<br>

- **Communicate over MQTT protocol to simulate a TRUMA INETBOX**
- **The requirements are a CPplus with a version number > C4.00.00 (see disclaimer-section)**
- **Input credentials over web-frontend**
- **Test mqtt-connectivity and lin-interface in web-frontend**
- **OTA-updating support with releasing (currently 2.1.x)**
- **Tested with both ports (ESP32 / RP2 pico w 2040)**
- **Include add-on: Optional Truma DuoControl over GPIO-connections**
- **Include add-on: Optional MPU6050 Sensor for spiritlevel-feature**

## Motivation and background
The possibilities opened up by controlling the RV heating via an mqtt-broker are manifold. The limits set by a simple SMS technology from the manufacturer are falling.  
It is very important to me to show here an ***out of the box*** solution that opens up these possibilities to everyone simply and easily - without special electrical and without programming knowledge. If you don't have the confidence to assemble the few components yourself, you can also ask me for ready-made modules.

The current version opens up a very flexible debugging and also the possibility to write log-files to specify problems and solve them as quickly as possible.

If you like this software and even use it, then I deserve a beer. Thanks for that in advance. You will find the Sponsorship button on the right-hand side for this purpose.

## Acknowledgement
The software is based on the Github project [INETBOX](https://github.com/danielfett/inetbox.py) by Daniel Fett.
Thanks to him, as well as the preliminary work of [WoMoLIN](https://github.com/muccc/WomoLIN), these cool projects have become possible.

This project here was developed and tested for an ESP32 (first generation) with 4 MB memory. The software also works on other ESP32 models and probably, with small adjustments (UART address, pins), also on other hardware. The tests on a Raspberry Pi Pico W were successful, too. I will not always explicitly mention the RP2 pico w in the following. The respective points apply to this chip as well. The minor deviations can be found at the end in the section **Running on RP2 Pico W** for details. 

## Disclaimer
I have tested my solution for the ESP32/RP2 pico in more than 15 different environments so far, including my own TRUMA/CPplus version. Most of the tests ran straight *out of the box*. 

Please note that older versions of CPplus (e.g. C3.xx.xx) use a different protocol for communication with the inetbox. See the INIT menu <[example given](https://videopress.com/embed/oXHpx1Ge)> on the CPplus to find the version numbers. Therefore, the data can be read but no commands can be set. If you still want to use the inetbox2mqtt, you can replace the CPplus with a newer one (e.g. C4.03.00). New CPplus can also control older TRUMA heaters (e.g. H5.xx.xx). Several users have successfully taken this step, so the procedure can be recommended.

Please ensure that your tests are carried out with a clean electrical setup, preferably already in the *proof of concept* phase in a stable housing, in order to prevent short circuits or bad connections. Since the LIN connection has a plug, it is advisable to also realise the power supply via a plug. Most problems during realisation can be traced back to defective components due to short circuits or missing ground connections

Please note that this simulation only works on a CPplus to which **NO** Inetbox is connected. In particular, communication with a **TRUMA INet X** is not supported.
**TRUMA INet X** is the successor of CPplus and contains inetbox functionalities

The LIN module for the ESP32/RP2 pico in the current version for the ESP32/RP2 pico w have proven to be very stable and CPplus-compatible. It's been going on for months now in various constellations.


**Nevertheless, it should be mentioned here that I do not assume any liability or guarantee for its use.**

## Electrics
There is no 12V potential at the RJ12 (LIN connector). Therefore, the supply voltage must be obtained separately from the car electrical system. 

The electrical connection via the TJA1020 to the UART of the ESP32/RP2 pico is made according to the circuit diagram shown. It is important to connect not only the signal level but also the ground connection. 

<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/206511684-806cda73-a47d-4070-86ac-6de7d999c5d6.png)

</div>

Examples for the implementation of the concrete connection can be found under [Connection](https://github.com/mc0110/inetbox2mqtt/issues/20).

On the **ESP32** we recommend the use of UART2 (**Tx - GPIO17, Rx - GPIO16**):

<div align = center>

![1](https://user-images.githubusercontent.com/65889763/200187420-7c787a62-4b06-4b8d-a50c-1ccb71626118.png)

</div>

On the **RP2 pico w** we recommend the use of UART1 (**Tx - GPIO04, Rx - GPIO05**):

<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/201338579-29c815ca-e5ef-4f25-b015-1749a59b3e99.png)
</div>

These are to be connected to the TJA1020. No level shift is needed (thanks to the internal construction of the TJA1020). It also works on 3.3V levels, even if the TJA1020 is operated at 12V. 


## Installation instructions

### MicroPython
The software is developed in micropython. After the first tests, I was amazed af how good and powerful the [microPython.org](https://docs.micropython.org/en/latest/) platform is. 

However, the software did not run with the latest stable kernel from July (among other things, the bytearray.hex was not implemented there yet). The latest kernels for various ports can be found in the [download section](https://micropython.org/download/). It is quite possible that the software can also run on other ports. If you have had this experience, please let us know. We can then amend the readme accordingly.


### Alternative 1: OTA-Installation with mip
If you just want to get the inetbox2mqtt running on the RP2 pico w, this is the way to go. 

If you have ESP32 with larger memory, you can try this way as well. Since I haven't tested this myself, feel free to give me feedback. 

For the simple 4M types of the ESP32-S this way does not work anymore. Here I ask you to use alternative 2.

The entire installation process should not take longer than 10 minutes. The installation does not have to take place in the final WLAN in which the inetbox2mqtt is to run later.

To do this, you first have to install an up to date microPython version, to be found at [micropython/download](https://micropython.org/download/). My tests were done with upython-version > 19.1-608.

The way I am following at the moment is:

- Install Micropython on the port
- Wifi connection via terminal
- Loading the web application via terminal

You must enter the commands from the console line by line in the REPL interface. The last import command reloads the entire installation.

    import network
    st = network.WLAN(network.STA_IF)
    st.active(True)
    st.connect('<yourSSID>','<YourWifiPW>')
    import mip
    mip.install('github:mc0110/inetbox2mqtt/bootloader/main.py','/')
    import main


### Alternative 2: With esptool - only works with the ESP32
The ESP32 with 4M memory does not have enough main storage in the standard micropython firmware to have all the software in memory. For this reason, some of the python modules have been precompiled and are already included in the firmware. Therefore, it is recommended to use the .bin file. Of course, all source files of the project are included, so that anyone can create the micropython firmware himself.

The .bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:

    esptool.py write_flash 0 flash_esp32_inetbox2mqtt_v210_4M.bin

This is not a partition but the full image for the ESP32 and only works with the 4MB chips. The address 0 is not a typo.

## Releasing and updating
There are two release numbers that must match, one in main.py and one in release.py. The update process looks at this and if the numbers are different, then the software is updated during the update.

We are very keen to support the application in the best possible way. Most of the changes were necessary to enable the realisation of a web frontend and the initial installation, the entry of the login data for Wifi connection and mqtt-broker and to test this connection and, from version 2.1.x, also to be able to test the LIN connection to CPplus. It is recommended as best practice to reinstall the application in the process if updating is also possible.

**ATTENTION:** 
- RP2 pico: The change to version 2.1.0 requires an interaction via the web frontend. Please delete the file cred.py in the file manager of the web frontend first, then start the update process. 
- ESP32-4M: Version 2.1.0 only works with the precompiled firmware. With the firmware, however, later updates are also possible.


## Web frontend
After rebooting the port (ESP32, RP2 pico w), an access point (ESP or PICO) is opened first. For the RP2 pico w, the password "password" is required. Please first establish a Wifi connection with the access point. Then you can access the chip in the browser at http://192.168.4.1 and enter the credentials. For details of the Wifimanager, please refer to [mc0110/wifimanager](https://github.com/mc0110/wifimanager).

We call this the **OS mode** -> i.e. an operating mode that is not the normal run mode but is necessary for tests and for entering the login data.

<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/214956414-b75eac0a-83a4-40ee-a858-b499fe4f3b97.png)

</div>

You have access to the entire file system with up, download and delete functions via a simple file manager. 

You can also test the connectivity to the MQTT broker.

As of version 2.1.x, the LIN module - responsible for the TRUMA communication - is already fully executable in this mode. This is very helpful for debugging the electrical connection or for any adjustments.

In this mode, the TRUMA status elements can be queried about the overall status (see button STATUS) and the set command for the water heater (ON / OFF) can be set via buttons.

You can now also carry out the INIT process in this mode. Details are described below.

### Credentials formular

<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/213916483-5de8220b-5562-400e-91f1-5ffc76c1bb14.png)
</div>

After entering the login credentials, the boot mode can be switched from "OS-Run" to "normal-run". The button toggles between the two states.

After rebooting in "normal-run" mode, inetbox2mqtt is ready for use.

For placing the files and creating the credentials on the port, it does not need to be connected to the CPplus. You can also swap between 2 different credential-files, e.g. you are working on your computer at home for configuring and then swap to the RV-credentials in your motorhome.

If everything is correctly set up and the port is rebooted, it should connect to the MQTT broker with a 2 confirmation messages.

## INIT - RESET process

Now you can establish the connection between the port and the LIN bus. 

The inetbox2mqtt must be registered once with the CPplus. This initialisation process is very important and without it the connection will not be established successfully. 

Inetbox2mqtt must be in normal-run mode when you initialise the CPplus.

*Let's have one further look at the INIT process:* 

Without inetbox2mqtt you find 2 entries in the INIT menu:

- TRUMA: Hx.00.nn
- CPplus: Cy.0z.00

### Start INIT process

To do this you have to select and confirm the menu item RESET in the CPplus menu and then also confirm the PR SET that appears. The display then shows a flickering INIT... -> [example given](https://videopress.com/v/xsPXCWr3).

If the INIT process was successful, then a third entry appears in the INIT menu for the inetbox

- TRUMA: Hx.00.nn
- CPplus: Cy.0z.00
- inetbox: T23.70.0

This process has to be carried out once, after which the connection can be terminated at any time and then resumed as long as no further INIT (RESET at CPplus) takes place.

***Very, very important:*** 

If you have already connected an inetbox to the CPplus, it is essential to carry out the INIT once without the inetbox. After that, there should only 2 entries be displayed. Then you can connect the inetbox2mqtt to perform another INIT.


## MQTT topics

The ***service/truma/control_status/#*** topics can be received. They include the current status of CPplus and TRUMA 
If your heater is off and you start with a set-command or with an input at the CPplus there is a delay of about 30sec before you'll see the first values. This is a normal behavior.


| Status Topic | Payload | Function |
--------|---------|----------|
| service/truma/control_status/# ||subcribing all status-entries|
| service/truma/control_status/alive|on/off|connection control|
| service/truma/control_status/clock| hh:mm| CPplus time|
| service/truma/control_status/release| x.y.z| release no|
| service/truma/control_status/current_temp_room| temperature in °C (0, 5-30°C)| show current room temperature|
| service/truma/control_status/target_temp_room| temperature in °C (0, 5-30°C)| show target room temperature|
| service/truma/control_status/current_temp_water| temperature in °C (0-70°C)| show current water temperature|
| service/truma/control_status/target_temp_water| temperature in °C (0-70°C)| show target water temperature|
| service/truma/control_status/energy_mix| gas, mix, electricity| mode of operation|
| service/truma/control_status/el_power_level| 0, 900, 1800| electrical max. consumption|
| service/truma/control_status/heating_mode| off, eco, high| fan state|
| service/truma/control_status/operating_status| 0 - 7| internal operation-mode (0,1 = off / 7 = running)|
| service/truma/control_status/error_code| 0-xx| TRUMA error codes|
| service/truma/control_status/release| xx.xx.xx| Software-Release-No|


If you want to set values, then you must use the corresponding set-topics. The list of set-topics and valid payloads can be found here.


| Set Topic | Payload | Function |
--------|---------|----------|
| service/truma/set/target_temp_room| temperature in °C (0, 5-30°C)| set target room temperature|
| service/truma/set/target_temp_water| 0, 40, 60, 200| set target water temperature (= off, eco, high, boost)|
| service/truma/set/energy_mix| gas, mix, electricity| set mode of operation|
| service/truma/set/el_power_level| 0, 900, 1800| set electrical max. consumption|
| service/truma/set/heating_mode| off, eco, high| set fan state (off only accepted, if room heater off)|
| **System commands** | |
| service/truma/set/reboot| 1| reboot the port|
| service/truma/set/os_run| 1| set mode OS-RUN|
| service/truma/set/ota_update| 1| download current version from GITHUB|


To switch on the room heating, target_temp_room > 4 and heating_mode = eco must be set together. For this purpose, the respective commands should be sent immediately after each other. 

The same applies to energy_mix and el_power_level, which should be set together. 

For further explanation see command usage [INETBOX](https://github.com/danielfett/inetbox.py). 

The system commands are an extension of the command scope and allow restarting the port, changing the operating mode and updating the software status with the GITHUB release. 

An [example](https://github.com/mc0110/inetbox2mqtt/tree/main/doc) for a complete control system of a Smart Home solution can be found in the Docs - it shows the capability of bidirectional operation of Home Assistant. Bidirectional means that the values can be set in the CPplus display as well as in the Home Assistant frontend and are passed through in each case.

## Status LEDs are showing the operating mode

The operating mode is indicated by 2 GPIO outputs. This gives the option of displaying the current mode with 2 LEDs. The LEDs are to be connected in negative logic:

<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/209949544-1eac67dc-dc59-463a-9d05-04cbe6861b6d.png)

</div>


GPIO12 indicates when the MQTT connection is up. 

GPIO14 indicates when the connection to the CPplus is established.

The search for ***connection errors*** (e.g. missing LIN signal, swapping rx/tx, defective TJA 1020) can be very time-consuming and annoying. Therefore GPIO14 has been supplemented to the extent that the LED already flickers slightly when signals are registered on the port rx line (equivalent is tx-output on the TJA 1020). This also happens before an ***CPplus INIT***, in other words a registration of the inetbox2mqtt at the CPplus has taken place. In this way, it can be detected very quickly whether there are connection problems on the rx line. If the INIT process has taken place, the LED lights up brightly. 

*Attention: The CPplus does not transmit continuously, therefore transmission pauses of 15-25s are normal.* 

## Addon: Integration of Truma DuoControl
Another functionality has been added. This is an additional function, at the moment not implemented in [INETBOX](https://github.com/danielfett/inetbox.py). 

<div align = center>


![grafik](https://user-images.githubusercontent.com/10268240/209955598-e75b7240-bfaf-43e4-a554-82e53861f494.png)

</div>

The status changes of two GPIO inputs (GPIO18 and GPIO19) and the GPIO outputs (GPIO22 and GPIO23) are now also published to the broker. The reaction time for status-changes is approx. 10s. 

The associated topics are

- service/truma/control_center/duo_ctrl_gas_green
- service/truma/control_center/duo_ctrl_gas_red
- service/truma/control_center/duo_ctrl_i
- service/truma/control_center/duo_ctrl_ii

with the payloads ON/OFF. The outputs can be controlled with the SET commands

- service/truma/set/duo_ctrl_i
- service/truma/set/duo_ctrl_ii

Inputs and outputs are inverted, i.e. the inputs react with ON when connected to GND, the outputs switch to GND level when ON.

## Addon: Integration of MPU6050 for spiritlevel-Feature
A second optional feature has been added. For leveling of an RV-car a
MPU6050 IMU (inertial measurement unit) can be connected to the I2C bus. 

*Attention: The original version of this add-on used the GPIO00/01 for the I2C communication. Unfortunately, there is a conflict with the system UART (Tx=GPIO01). As a consequence, no debugging output was possible after initialising the I2C interface. It is important for all those who want to update to the current version that the pins for SDA and SCL have changed!*

Different pins are required here:

For **ESP32** please use I2C bus with SDA (GPIO26) and SCL (GPIO25).
For **RP2 pico w** please use I2C bus 1 with SDA (GPIO02) and SCL (GPIO03).

Every 500ms the acceleration and gyroscopic values are read and combined and filtered by a [Kalman-Filter](https://www.navlab.net/Publications/Introduction_to_Inertial_Navigation_and_Kalman_Filtering.pdf).
For the moment the result (pitch and roll angle) is published via MQTT
every 10s.

The associated topics are

- service/spiritlevel/spirit_level_pitch
- service/spiritlevel/spirit_level_roll

## Alive topic
Short digression: The CPplus only sends 0x18 (with parity it is 0xD8) requests if an INETBOX is registered. This can be recognised by the third entry in the index menu on the CPplus, among other things. The port answers these requests. Only when it receives 0x18 messages, the connection to the CPplus is established and the registration has taken place. This makes it easy to find out if there is an electrical problem. If the LED (GPIO14, see Status LEDs) is lit, communication with the CPplus is established. The port also outputs this as an "alive" topic via the MQTT connection (approx. every 60 sec): connection OK => payload: ON; connection not OK => payload: OFF.

## Good news for Home Assistant users
To make it even easier to set up the INETBOX simulator together with the [Home Assistant](https://www.home-assistant.io/) smarthome system, the [auto-discovery function of home assistant](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) is implemented.

After the port has connected to the MQTT broker, it sends the installation codes. If the Home Assistant server is also connected to the MQTT broker, the entities are all generated automatically. They all begin with 'truma_'. Since they are not persistent, this automatic generation also takes place when the Home Assistant server is restarted.

The Home Assistant's own MQTT broker, which is available as an add-on, can also be used. If you use other smart home systems, you can simply ignore the messages. In the [docs](https://github.com/mc0110/inetbox2mqtt/tree/main/doc), there is an example of a frontend solution in Home Assistant.



## Running on a RP2 pico W
Micropython can be installed very easily on the RP2 pico W. Please use a current release (younger than 19.1 Oct.22) of Python here - analogous to the note for the ESP32. The installation is explained very well on the [Foundation pages](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html).
 
Fortunately, the entire **inetbox2mqtt** software also runs on this port. Please note, as mentioned above, that the UART uses different pins. Since the GPIO pins for the support leds are present on the RPi-board, just like the GPIO pins for the connection to the Truma DuoControl, no changes are necessary here. The hardware is recognized by the software, therefore 
nothing is to do. If you want to use the **spiritlevel-addon**, then please note the corresponding pins for SDA (GPIO2) for SCL (GPIO3).

Experience currently shows that the micropython wifi connection with the PI2 pico w is not optimal. The ESP32 is much more stable. This makes the update process for the pico more of a lottery and should only be carried out under control. On the other hand, the RP2 pico has a larger memory and is otherwise very robust in operation. 

Everyone should decide for themselves what is more important to them, especially since the RP2 pico w boards are much smaller than the breakboards for the ESP32.
