# Image V084: including the Truma duo control and mpu6050 functionalities 

The .bin file contains both the python and the .py files. This allows the whole project to be flashed onto the ESP32 in one go. For this, you can use the esptool. In my case, it finds the serial port of the ESP32 automatically, but the port can also be specified. The ESP32 must be in programming mode (GPIO0 to GND at startup). The command to flash the complete .bin file to the ESP32 is:


      esptool.py write_flash 0 flash_dump_esp32_lin_v0842_4M.bin


This is not a partition but the full image for the ESP32 and only works with the 4MB chips. The address 0 is not a typo.

After flashing, please reboot the ESP32 and connect it to a serial terminal (e.g. miniterm, putty, serialport) (baud rate: 115700) fur further steps like checking if everything is working ok.
