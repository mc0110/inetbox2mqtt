<div align = center>

# inetbox2mqtt
## Control your TRUMA heater over a MQTT broker

### microPython version for ESP32 and RP pico w
<br/>

[![Badge License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt)
 &nbsp;
[![Badge Version](https://img.shields.io/github/v/release/mc0110/inetbox2mqtt?include_prereleases&color=yellow&logo=DocuSign&logoColor=white)](https://github.com/mc0110/inetbox2mqtt/blob/main/README.md)
 &nbsp; 
![Badge Hit Counter](https://visitor-badge.laobi.icu/badge?page_id=https://github.com/mc0110/inetbox2mqtt/README.md)
<br/><br/>
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)

</div>
<br>

- **communicate over MQTT protocol to simulate a TRUMA INETBOX**
- **include optional Truma DuoControl over GPIO-connections**
- **include optional MPU6050 Sensor for spiritlevel-feature**
- **input credentials over web-frontend**
- **OTA-updating implemented**
- **tested with both ports (ESP32 / RPi pico w 2040)**

## Acknowledgement
The software is a derivative of the github project [INETBOX](https://github.com/danielfett/inetbox.py) by Daniel Fett. 
Thanks to him, as well as the preliminary work of [WoMoLIN](https://github.com/muccc/WomoLIN), these cool projects have become possible.

This project here was developed and tested for an ESP32 (first generation) with 4 MB memory. The software also works on other ESP32 models and probably, with small adjustments (UART address, pins), also on other hardware. The tests on a Raspberry Pi Pico W were successful, too. I will not always explicitly mention the RPi pico w in the following. The respective points apply to this chip as well. The minor deviations can be found at the end in the section **Running on RPI Pico W** for details. 

## Disclaimer
I have tested my solution for the ESP32 in about 10 different environments so far, including my own TRUMA/CPplus version. Most of the tests ran straight out of the box. 

The LIN module for the ESP32/RPi pico in the current version for the ESP32/RPI pico w have proven to be very stable and CPplus-compatible. It's been going on for months now in various constellations.

**Nevertheless, it should be mentioned here that I do not assume any liability or guarantee for its use.**

## Electrics
There is no 12V potential at the RJ12 (LIN connector). Therefore, the supply voltage must be obtained separately from the car electrical system. 

The electrical connection via the TJA1020 to the UART of the ESP32/RPI pico is made according to the circuit diagram shown. It is important to connect not only the signal level but also the ground connection. 
<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/206511684-806cda73-a47d-4070-86ac-6de7d999c5d6.png)

</div>

For examples of connection errors, please refer to [Connection Errors](https://github.com/mc0110/inetbox2mqtt/issues/20). Please refer also for more details of the project [INETBOX](https://github.com/danielfett/inetbox.py) mentioned above. 

On the **ESP32** we recommend the use of UART2 (**Tx - GPIO17, Rx - GPIO16**):

<div align = center>

![1](https://user-images.githubusercontent.com/65889763/200187420-7c787a62-4b06-4b8d-a50c-1ccb71626118.png)

</div>

On the **RPI pico w** we recommend the use of UART1 (**Tx - GPIO04, Rx - GPIO05**):

<div align = center>

![grafik](https://user-images.githubusercontent.com/10268240/201338579-29c815ca-e5ef-4f25-b015-1749a59b3e99.png)
</div>

These are to be connected to the TJA1020. No level shift is needed (thanks to the internal construction of the TJA1020). It also works on 3.3V levels, even if the TJA1020 is operated at 12V. 

## MQTT topics - almost the same, but not exactly the same

The ***service/truma/control_status/#*** topics can be received. They include the current status of CPplus and TRUMA 
If your heater is off and you start with a set-command or with an input at the CPplus there is a delay of 1-2min before you'll see the first values. This is a normal behavior.


| Status Topic | Payload | Function |
--------|---------|----------|
| service/truma/control_status/# ||subcribing all status-entries|
| service/truma/control_status/alive|on/off|connection control|
| service/truma/control_status/clock| hh:mm| CPplus time|
| service/truma/control_status/current_temp_room| temperature in °C (0, 5-30°C)| show current room temperature|
| service/truma/control_status/target_temp_room| temperature in °C (0, 5-30°C)| show target room temperature|
| service/truma/control_status/current_temp_water| temperature in °C (0-70°C)| show current water temperature|
| service/truma/control_status/target_temp_water| temperature in °C (0-70°C)| show target water temperature|
| service/truma/control_status/energy_mix| gas, mix, electricity| mode of operation|
| service/truma/control_status/el_power_level| 0, 900, 1800| electrical max. consumption|
| service/truma/control_status/heating_mode| off, eco, high| fan state|
| service/truma/control_status/operating_status| 0 - 7| internal operation-mode (0,1 = off / 7 = running)|
| service/truma/control_status/error_code| 0-xx| TRUMA error codes|



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
| service/truma/set/run_os| 1| set mode OS-RUN|
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

## Integration of Truma DuoControl
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

## Integration of MPU6050 for spiritlevel-Feature
A second optional feature has been added. For leveling of an RV-car a
MPU6050 IMU (inertial measurement unit) can be connected to the I2C bus. 

*Attention: The original version of this add-on used the GPIO00/01 for the I2C communication. Unfortunately, there is a conflict with the system UART (Tx=GPIO01). As a consequence, no debugging output was possible after initialising the I2C interface. It is important for all those who want to update to the current version that the pins for SDA and SCL have changed!*

Different pins are required here:

For **ESP32** please use I2C bus with SDA (GPIO26) and SCL (GPIO25).
For **RPI pico w** please use I2C bus 1 with SDA (GPIO02) and SCL (GPIO03).

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

## MicroPython
After the first tests, I was amazed af how good and powerful the [microPython.org](https://docs.micropython.org/en/latest/) platform is. However, the software did not run with a kernel from July (among other things, the bytearray.hex was not implemented there yet).


## Installation instructions

### Alternative 1: OTA-Installation with mip
If you just want to get the inetbox2mqtt running, this is the way to go, and it works for both ports. This is also the fastest way, because the entire installation process should not take longer than 10 minutes. The installation does not have to take place in the final WLAN in which the inetbox2mqtt is to run later.

To do this, you first have to install an up to date microPython version, to be found at [micropython/download](https://micropython.org/download/). My tests were done with upython-version > 19.1-608.

The way I am following at the moment is as follows:

- Install Micropython on the port
- Wifi connection via terminal
- loading the web application via terminal

You must enter the commands from the console line by line in the REPL interface. The last import command reloads the entire installation.

    import network
    st = network.WLAN(network.STA_IF)
    st.active(True)
    st.connect('<yourSSID>','<YourWifiPW>')
    import mip
    mip.install('github:mc0110/inetbox2mqtt/bootloader/main.py','/')
    import main


### Alternative 2: With esptool - only works with the ESP32
The .bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:

    esptool.py write_flash 0 flash_esp32_inetbox2mqtt_v13_4M.bin

This is not a partition but the full image for the ESP32 and only works with the 4MB chips. The address 0 is not a typo.

After flashing, please reboot the ESP32 and connect it to a serial terminal (e.g. miniterm, putty, serialport) (baud rate: 115200) fur further steps like checking if everything is working ok.


### Credentials
After rebooting the port (ESP32, RPI pico w), an access point (ESP or PICO) is opened first. For the RPI pico w, the password "password" is required. Please first establish a Wifi connection with the access point. Then you can access the chip in the browser at http://192.168.4.1 and enter the credentials. For details of the Wifimanager, please refer to [mc0110/wifimanager](https://github.com/mc0110/wifimanager).

After entering the credentials, the boot mode can be switched from "OS-Run" to "normal-run". The button toggles between the two states.

After rebooting in "normal-run" mode, inetbox2mqtt is ready for use.

For placing the files and creating the credentials on the port, it does not need to be connected to the CPplus. You can also swap between 2 different credential-files, e.g. you are working on your computer at home for configuring and then swap to the RV-credentials in your motorhome.

If everything is correctly set up and the port is rebooted, it should connect to the MQTT broker with a 2 confirmation messages.

Then you can establish the connection between the port and the LIN bus. This connection is not critical and can be disconnected at any time and then re-established. It should not be necessary to re-initialise the CPplus.

### Running on a RPi pico W
Micropython can be installed very easily on the RPI pico W. Please use a current release (younger than 19.1 Oct.22) of Python here - analogous to the note for the ESP32. The installation is explained very well on the [Foundation pages](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html).
 
Fortunately, the entire **inetbox2mqtt** software also runs on this port. Please note, as mentioned above, that the UART uses different pins. Since the GPIO pins for the support leds are present on the RPi-board, just like the GPIO pins for the connection to the Truma DuoControl, no changes are necessary here. The hardware is recognized by the software, therefore 
nothing is to do. If you want to use the **spiritlevel-addon**, then please note the corresponding pins for SDA (GPIO2) for SCL (GPIO3).

Unfortunately, the web frontend does not work very well. Even if no errors occur, the response times to browser requests are sometimes very delayed.

 Since the software runs perfectly on the ESP32, I suspect there is still a bug in the uasyncio module. So if you are using this chip, please be patient. However, it is still possible to enter the credentials with this chip without any problems. 
 
 Only the OTA loading concept does not work via browser or MQTT command. The behaviour of the port is very different from the behaviour of the ESP32. With the ESP32, the OTA process works perfectly.
