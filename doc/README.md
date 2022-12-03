# Example of a front-end realisation
Control of the TRUMA CPplus with a lovelance card in home assistant

![grafik](https://user-images.githubusercontent.com/10268240/205453364-b1dbf6ee-b9e2-4b22-9816-325be939b3a4.png)

You find the lovelance-card also as file in this directory. 
You need the corresponding truma.yaml file in the configuration.yaml or in a separate file. 

About the function of the card: 

The upper part shows the status of the CPplus. In the lower part, the hot water (a climate entity is also generated for this) can be selected via the buttons. In the function, the hot water production is automatically switched off when the target temperature is reached.
The room thermostat lets the TRUMA take over the temperature control. If the room temperature is changed, the changed temperature is communicated to the TRUMA. Since the TRUMA can only set the temperature to within one degree (Celsius), the target temperature is rounded off accordingly by the thermostat element. The heating can be switched off via the thermostat. Furthermore, the operating modes of the TRUMA (gas, mixed, electric) can be preselected. In addition to the PRESETS, the heating can also be controlled very easily via automations using the climate.set_temperature service.

    type: vertical-stack
    cards:
    - type: entity
        entity: sensor.truma_clock
        name: TRUMA Zeit
    - show_name: false
        show_icon: true
        show_state: true
        type: glance
        entities:
        - entity: sensor.truma_heating_mode
            name: Lüfter
            icon: mdi:fan-auto
        - entity: sensor.truma_energy_mix
            name: Energie
            icon: mdi:fuel-cell
        - entity: sensor.truma_el_power_level
            name: El-Mode
            icon: mdi:lightning-bolt-outline
        columns: 3
        title: Status
    - show_name: false
        show_icon: true
        show_state: true
        type: glance
        entities:
        - entity: sensor.truma_operating_status
            name: Mode
            icon: mdi:state-machine
        - entity: sensor.truma_error_code
            icon: mdi:head-question
        - entity: binary_sensor.truma_alive
            name: Lin-Kom
        - entity: sensor.truma_target_temp_room
        - entity: sensor.truma_target_temp_water
        columns: 3
    - type: horizontal-stack
        cards:
        - show_name: true
            show_icon: false
            type: button
            name: Hotwater
            tap_action:
            action: toggle
            entity: input_boolean.truma_water_switch
            show_state: true
        - type: button
            name: eco
            tap_action:
            action: call-service
            service: climate.set_temperature
            target:
                entity_id: climate.truma_water
            data:
                temperature: 40
            show_name: true
            show_icon: true
        - type: button
            name: hot
            tap_action:
            action: call-service
            service: climate.set_temperature
            target:
                entity_id: climate.truma_water
            data:
                temperature: 60
            show_name: true
            show_icon: true
        - type: button
            name: boost
            tap_action:
            action: call-service
            service: climate.set_temperature
            target:
                entity_id: climate.truma_water
            data:
                temperature: 65
            show_name: true
            show_icon: true
        title: Wasser
    - type: horizontal-stack
        cards:
        - show_name: false
            show_icon: true
            type: button
            name: FAN
            tap_action:
            action: toggle
            entity: input_boolean.truma_fan_mode
            show_state: true
            icon: mdi:fan
            icon_height: 60px
        title: Raumklima
    - type: thermostat
        entity: climate.truma
    - type: horizontal-stack
        cards:
        - show_name: true
            show_icon: true
            type: button
            tap_action:
            action: toggle
            entity: input_boolean.truma_heat_gas
            name: Gas
            icon: mdi:gas-burner
            show_state: true
        - show_name: true
            show_icon: true
            type: button
            name: Mix1
            tap_action:
            action: toggle
            entity: input_boolean.truma_heat_mix1
            icon: mdi:home-lightning-bolt-outline
            show_state: true
        - show_name: true
            show_icon: true
            type: button
            name: Mix2
            tap_action:
            action: toggle
            entity: input_boolean.truma_heat_mix2
            icon: mdi:home-lightning-bolt
            show_state: true
        - show_name: true
            show_icon: true
            type: button
            name: Elektrik
            tap_action:
            action: toggle
            entity: input_boolean.truma_heat_elec
            icon: mdi:home-lightning-bolt
            show_state: true
        title: Energie




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
