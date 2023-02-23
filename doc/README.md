# Example of a front-end realisation

First of all, I would like to ask you to send me **examples of your smarthome systems** so that we can publish them. It would be great if we could also show examples of e.g. openhab or node-red implementations here also. But alternatives to realisation in Home Assistant are of course also welcome.


## TRUMA heater - example for a frontend in Home Assistant

Since I use a Home Assistant system myself, you can currently only find the implementation of the mqtt-protocol-transfer in HA. 

The given truma.yaml is a package in the HA logic, so please note the explanations about [packages](https://www.home-assistant.io/docs/configuration/packages/) in the HA documentation.An example of fully control from a smart home solution as example of bidirectional operation from Home Assistant. 

Bidirectional means that the values can be set both in the CPplus display and in the home assistant frontend and are passed through in each case. 

## Lovelance frontend card in home assistant

![grafik](https://user-images.githubusercontent.com/10268240/206495832-0511af4f-29f3-4eaf-b196-728ea1779255.png)

You find the lovelance-card also as file in this directory. 

About the function of the card: 

The upper part shows the hot water (a climate entity is also generated for this) can be selected via the buttons. In the function, the hot water production is automatically switched off when the target temperature is reached.

The room thermostat lets the TRUMA take over the temperature control. If the room temperature is changed, the changed temperature is communicated to the TRUMA. Since the TRUMA can only set the temperature to within one degree (Celsius), the target temperature is rounded off accordingly by the thermostat element. The heating can be switched off via the thermostat.

The control / adjustments of hot water and room temperature can also be made via the CPplus, so communication is fully bidirectional. The entries made there are then also transferred to the HA entities.

Furthermore, the operating modes of the TRUMA (gas, mixed, electric) can be preselected. In addition to the PRESETS, the heating can also be controlled very easily via automations using the climate.set_temperature service.
In the lower part you can observe the status of the CPplus. 

## Celsius vs. Fahrenheit
This example works only if CPplus and Home Assistant are set to Celsius. Initial tests with systems set to Fahrenheit show problems. If someone could send their approaches to solving this, that would be great.


## Here is an example of a simple GAUGE implementation of the MPU6050 Leveling Wizard - also in Home Assistant

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



