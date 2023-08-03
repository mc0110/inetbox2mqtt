## Electrics
A LIN-UART converter is necessary for communication with the TRUMA CPplus. Since there are now several boards available for purchase that already have the converter integrated, I have moved the level converter topic to the documentation for all those who want to build the level converter themselves.

There is no 12V potential at the RJ12 (LIN connector). Therefore, the supply voltage must be obtained separately from the car electrical system. 

The electrical connection via the TJA1020 to the UART of the ESP32/RP2 pico is made according to the circuit diagram shown. 

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

**It is important to connect not only the signal level but also the ground connection.**

![Alt text](image.png)

Here you see an example with a missing ground connection. It cannot work like that.