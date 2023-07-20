# Image V2.5 0 for ESP32 

The flash_esp32_xxxx.bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:

      esptool.py write_flash 0 flash_esp32_inetbox2mqtt_v251_4M.bin

There is also a version for both WOMOLIN variants, version 1 and version 2. The yellow network led informs about mqtt-activities. In version 2 the normal setup supports LIN1

      esptool.py write_flash 0 flash_womolin_inetbox2mqtt_v251_4M.bin

This is not a partition but the full image for the ESP32 and only works with the 4MB chips. The address 0 is not a typo.

After flashing, please reboot the ESP32. It will start with an access point on IP 192.168.4.1. After connecting with wifi you can start a browser to http://192.168.4.1. Now you should input the credentials.
See the details in the README.md. After you have done everything, press the button for "normal run" and restart the chip. It will than start without web frontend. 

Note: *Since the ESP32 does not have enough memory, the micropython version used is already pre-compiled with several modules, which reduces the memory requirement. The micropython version has the release date of Juli 2023.*

