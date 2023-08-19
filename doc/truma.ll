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
      - show_name: true
        show_icon: true
        type: button
        tap_action:
          action: toggle
        entity: input_boolean.truma_heat_gas
        name: Gas
        icon: mdi:gas-burner
      - show_name: true
        show_icon: true
        type: button
        name: Mix 1kW
        tap_action:
          action: toggle
        entity: input_boolean.truma_heat_mix1
        icon: mdi:home-lightning-bolt-outline
      - show_name: true
        show_icon: true
        type: button
        name: Mix 2kW
        tap_action:
          action: toggle
        entity: input_boolean.truma_heat_mix2
        icon: mdi:home-lightning-bolt
      - show_name: true
        show_icon: true
        type: button
        name: El 1kW
        tap_action:
          action: toggle
        entity: input_boolean.truma_heat_elec1
        icon: mdi:home-lightning-bolt
      - show_name: true
        show_icon: true
        type: button
        name: El 2kW
        tap_action:
          action: toggle
        entity: input_boolean.truma_heat_elec2
        icon: mdi:home-lightning-bolt
    title: Energie
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
              action: toggle
            entity: input_boolean.truma_water_eco
            show_name: true
            show_icon: true
          - type: button
            name: hot
            tap_action:
              action: toggle
            entity: input_boolean.truma_water_hot
            show_name: true
            show_icon: true
          - type: button
            name: boost
            tap_action:
              action: toggle
            entity: input_boolean.truma_water_boost
            show_name: true
            show_icon: true
        title: Wasser
      - type: horizontal-stack
        cards:
          - type: entity
            entity: sensor.truma_current_temp_water
            name: Momentan
          - show_name: true
            show_icon: true
            type: button
            tap_action:
              action: toggle
            entity: input_boolean.truma_water_autooff
            icon: mdi:thermometer-auto
            icon_height: 40px
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
        show_state: true
        type: glance
        entities:
          - entity: sensor.truma_clock
            icon: m
            name: TRUMA
          - entity: binary_sensor.truma_alive
            name: Status
          - entity: sensor.truma_release
            icon: m
            name: Release
        columns: 3
        title: Status
