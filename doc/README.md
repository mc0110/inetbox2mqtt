# Example of a front-end realisation
Control of the TRUMA CPplus with a lovelance card in home assistant

![grafik](https://user-images.githubusercontent.com/10268240/205453364-b1dbf6ee-b9e2-4b22-9816-325be939b3a4.png)

You find the lovelance-card also as file in this directory. 
You need the corresponding truma.yaml file in the configuration.yaml or in a separate file. 

About the function of the card: 

The upper part shows the hot water (a climate entity is also generated for this) can be selected via the buttons. In the function, the hot water production is automatically switched off when the target temperature is reached.
The room thermostat lets the TRUMA take over the temperature control. If the room temperature is changed, the changed temperature is communicated to the TRUMA. Since the TRUMA can only set the temperature to within one degree (Celsius), the target temperature is rounded off accordingly by the thermostat element. The heating can be switched off via the thermostat. Furthermore, the operating modes of the TRUMA (gas, mixed, electric) can be preselected. In addition to the PRESETS, the heating can also be controlled very easily via automations using the climate.set_temperature service.
In the lower part you can observe the status of the CPplus. 


# Here is an example of a simple GAUGE implementation of the MPU6050 Leveling Wizard

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


Both examples show the automatically generated entities and works without automations, etc.
