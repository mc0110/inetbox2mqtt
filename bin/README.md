# Image V084: including the Truma duo control and mpu6050 functionalities 

The .bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:


      esptool.py write_flash 0 flash_dump_esp32_lin_v10_4M.bin


This is not a partition but the full image for the ESP32 and only works with the 4MB chips. The address 0 is not a typo.

After flashing, please reboot the ESP32. It will start with an access point on 192.168.4.1. After connecting with wifi you can start a browser to http://192.168.4.1. Now you should input the credentials. After you have done everything, press the button for "normal run" and restart the chip. It will than start without web frontend. 
