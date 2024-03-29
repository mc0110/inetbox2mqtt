# Image V2.6.5 for ESP32 and V2.6.4 for WOMOLIN ESP32 Interface V1 and V2

The flash_esp32_xxxx.bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:

      esptool.py write_flash 0 flash_esp32_inetbox2mqtt_v265_4M.bin

The address 0 is not a typo.

This image contains a first version that supports both the LAN port and WLAN use. Furthermore, static IP addresses or DHCP can now be set. There is also a version for both WOMOLIN variants, version 1 and version 2. The yellow network led informs about mqtt-activities and also about Lin-interface-communication. In version 2 the normal setup supports LIN1. If you want to support LIN2, the second LIN-decoder, you need to change in args.dat the entry hw=WOMOLIN to hw=WOMOLIN_LIN2:

      esptool.py write_flash 0 flash_womolin_inetbox2mqtt_v264_4M.bin


***The development of this software and also just the maintenance in the different variants has already cost many hours of time. This is only possible with your support. So if you use this software, I deserve more than a beer. Many thanks for this in advance. For this purpose, you will find the Sponsorship button on the right side of the page.***

After flashing, please reboot the ESP32. It will start with an access point on IP 192.168.4.1. After connecting with wifi you can start a browser to http://192.168.4.1. Now you should input the credentials.
See the details in the README.md. After you have done everything, press the button for "normal run" and restart the chip. It will than start without web frontend. 

Note: *Since the ESP32 does not have enough memory, the micropython version used is already pre-compiled with several modules, which reduces the memory requirement. The micropython version has the release date of Juli 2023.*

