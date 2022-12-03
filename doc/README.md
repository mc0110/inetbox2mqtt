# Example of a front-end realisation
Control of the TRUMA CPplus with a lovelance card in home assistant

![grafik](https://user-images.githubusercontent.com/10268240/205453364-b1dbf6ee-b9e2-4b22-9816-325be939b3a4.png)


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
        columns: 3
    - type: horizontal-stack
        cards:
        - type: entity
            entity: sensor.truma_current_temp_water
            name: Wasser
        - type: entity
            entity: sensor.truma_target_temp_water
            name: Ziel
        title: Temperaturen
    - type: horizontal-stack
        cards:
        - type: entity
            entity: sensor.truma_current_temp_room
            name: Raum
        - type: entity
            entity: sensor.truma_target_temp_room
            name: Ziel
    - type: entities
        entities:
        - entity: select.truma_set_roomtemp
            name: Raumtemperatur
        - entity: select.truma_set_heating_mode
            name: Lüfter-Mode (off, eco, high)
        title: Einstellung
    - type: entities
        entities:
        - entity: select.truma_set_energy_mix
            name: Energie_Mix (gas, electricity, mix)
        - entity: select.truma_set_el_power_level
            name: EL_Power (0, 900,1800)
    - type: entities
        entities:
        - entity: select.truma_set_warmwater
            name: Warmwasser (0, 40, 60, 200)




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
