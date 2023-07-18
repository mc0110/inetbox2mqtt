type: vertical-stack
cards:
  - show_name: true
    show_icon: true
    type: button
    tap_action:
      action: toggle
    entity: input_boolean.truma_ctrl
    icon: mdi:radiator
    icon_height: 40px
  - type: horizontal-stack
    cards:
      - type: entity
        entity: sensor.truma_clock
        icon: m
        name: TRUMA
      - show_name: true
        show_icon: true
        show_state: true
        type: glance
        entities:
          - entity: binary_sensor.truma_alive
            name: Status
        columns: 1
      - type: entity
        entity: sensor.truma_release
        icon: m
        name: Release
  - type: vertical-stack
    cards:
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
                temperature: 200
            show_name: true
            show_icon: true
        title: Wasser
      - type: horizontal-stack
        cards:
          - type: entity
            entity: sensor.truma_current_temp_water
            name: Momentan
          - type: entity
            entity: sensor.truma_target_temp_water
            name: Ziel
          - show_name: true
            show_icon: true
            type: button
            tap_action:
              action: toggle
            entity: input_boolean.truma_water_autooff
            icon: mdi:thermometer-auto
            name: AutoOff
  - type: horizontal-stack
    cards:
      - type: thermostat
        entity: climate.truma
    title: Raumklima
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
  - type: horizontal-stack
    cards:
      - show_name: false
        show_icon: true
        show_state: true
        type: glance
        entities:
          - entity: sensor.truma_energy_mix
            name: Energie
            icon: mdi:fuel-cell
          - entity: sensor.truma_el_power_level
            name: El-Mode
            icon: mdi:lightning-bolt-outline
        columns: 2
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
        columns: 2
    title: Status
  - type: horizontal-stack
    cards:
      - show_name: false
        show_icon: true
        show_state: true
        type: glance
        entities:
          - entity: sensor.truma_target_temp_room
            name: Target Room
            icon: mdi:home-thermometer
        columns: 1
      - show_name: false
        show_icon: true
        show_state: true
        type: glance
        entities:
          - entity: sensor.truma_target_temp_water_named
            name: Target Water
            icon: mdi:water-boiler-auto
        columns: 1
      - show_name: false
        show_icon: true
        show_state: true
        type: glance
        entities:
          - entity: sensor.truma_heating_mode
            name: Lüfter
            icon: mdi:fan-auto
        columns: 1
