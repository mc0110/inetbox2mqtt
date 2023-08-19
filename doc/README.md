# Example of a front-end realisation

First of all, I would like to ask you to send me **examples of your smarthome systems** so that we can publish them. It would be great if we could also show examples of e.g. openhab or node-red implementations here also. But alternatives to realisation in Home Assistant are of course also welcome.


## TRUMA heater and Aventa AirCon - example for frontends in Home Assistant

Since I use a Home Assistant system myself, you can currently only find the implementation of the mqtt-protocol-transfer in HA. 

The given truma.yaml is a package in the HA logic, so please note the explanations about [packages](https://www.home-assistant.io/docs/configuration/packages/) in the HA documentation.An example of fully control from a smart home solution as example of bidirectional operation from Home Assistant. 

Bidirectional means that the values can be set both in the CPplus display and in the home assistant frontend and are passed through in each case. 

## Lovelance frontend cards in home assistant
### TRUMA heater

![grafik](https://github.com/mc0110/inetbox2mqtt/assets/10268240/b1c4a1a1-2010-4d82-beb7-28aea156389f)


### TRUMA aircon

![grafik](https://github.com/mc0110/inetbox2mqtt/assets/10268240/a70454ac-5690-4fed-965a-a8ca04f57a06)


You find both lovelance-cards also as file in this directory. 

About the function of the card:

New!: There is a central switch function integrated. So you can switch off and block all functions with one switch.

The upper part shows the hot water (a climate entity is also generated for this) can be selected via the buttons. In the function, the hot water production is automatically switched off when the target temperature is reached.

The room thermostat lets the TRUMA take over the temperature control. If the room temperature is changed, the changed temperature is communicated to the TRUMA. Since the TRUMA can only set the temperature to within one degree (Celsius), the target temperature is rounded off accordingly by the thermostat element. The heating can be switched off via the thermostat.

The control / adjustments of hot water and room temperature can also be made via the CPplus, so communication is fully bidirectional. The entries made there are then also transferred to the HA entities.

Furthermore, the operating modes of the TRUMA (gas, mixed, electric) can be preselected. In addition to the PRESETS, the heating can also be controlled very easily via automations using the climate.set_temperature service.

In the lower part you can observe the status of the CPplus. This part is without functionality and can be omitted.

## Celsius vs. Fahrenheit
This example works only if CPplus and Home Assistant are set to Celsius. Initial tests with systems set to Fahrenheit show problems. If someone could send their approaches to solving this, that would be great.

## ESPHOME version
For all those who are looking for an ESPHome version, I would like to refer to the great work of Fabian [esphome-truma_inetbox](https://github.com/Fabian-Schmidt/esphome-truma_inetbox), who has managed the realisation in this framework. Here, the MQTT protocol is no longer necessary, but it works via the HA-internal protocol.


## Example of a simple GAUGE implementation of the MPU6050 Leveling Wizard - also in Home Assistant

![grafik](https://user-images.githubusercontent.com/10268240/202903478-bbf7741f-cc21-48a2-918b-e94c15f7c373.png)

            title: test-imu 
                  - type: gauge
                    entity: sensor.pan1pitch
                    min: -20
                    max: 20
                    needle: true
                    name: Pitch
                    unit: °
                  - type: gauge
                    entity: sensor.pan1roll
                    name: Roll
                    unit: °
                    min: -20
                    max: 20
                    needle: true



