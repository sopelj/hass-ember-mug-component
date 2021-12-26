# [Ember Mug Integration for Home Assistant](https://github.com/sopelj/hass-ember-mug-component)

[![GitHub Release](https://img.shields.io/github/release/sopelj/hass-ember-mug-component.svg?style=for-the-badge)](https://github.com/sopelj/hass-ember-mug-component/releases)
[![License](https://img.shields.io/github/license/sopelj/hass-ember-mug-component.svg?style=for-the-badge)](LICENSE.md)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
![Project Maintenance](https://img.shields.io/maintenance/yes/2021.svg?style=for-the-badge)

Custom integration for the Ember Mug in Home Assistant.
I only have the Ember Mug 2, but in theory it should be the same with other Ember Mugs.

The protocol is not public, so there is quite a bit of guesswork involved.
[@orlopau](https://github.com/orlopau) has documented the most important [UUIDs here](https://github.com/orlopau/ember-mug)
Some of it I had to get from the Android App.

This is still a work in progress, but seems to be working for reading information at least.

## Installation

Add to HACS as custom repository:

<https://github.com/sopelj/hass-ember-mug-component>

And then add to your configuration.yaml and add sensors for your mug(s):

```yaml
sensors:
  - platform: ember_mug
    mac: C9:0F:59:D6:33:F9  # Replace with your Mug's MAC address
    name: "Jesse's Ember Mug"  # Optional Name
    temperature_unit: "C"  # Optional: Default [C]
```

### Caveats / known issues:

- The services to change mug values fail with a bluetooth permission error, that I can't figure out yet. 
- If you have another device paired with it like your phone it will cause it to disconnect, so you need to remove it from that device.
- If it won't connect you may need to go back into pairing mode (Hold down 5 seconds until light flashes blue).
- This maintains a connection to your mug which:
    - may affect battery
    - may interfere with other local bluetooth integrations as it can only maintain one connection at a time.

## Automations:

If you want to have notifications similar to the app you can do something like:

```yaml
automation:
  - id: mug_filled
    alias: Mug Filled
    trigger:
      - platform: state
        entity_id: sensor.jesse_s_ember_mug  # your mug entity
        attribute: liquid_state
        from: "Empty"
        to:
          - "Filling"
          - "Heating"
          - "Cooling"
    action:
      service: notify.mobile_app_jesse_s_pixel_4a  # Mobile device notify or other action
      data:
        message: Your mug has been filled

  - id: mug_temp_right
    alias: Mug Temp is right
    trigger:
      - platform: state
        entity_id: sensor.jesse_s_ember_mug  # your mug entity
        attribute: liquid_state
        from:
          - "Heating"
          - "Cooling"
        to: "Perfect"
    action:
      service: notify.mobile_app_jesse_s_pixel_4a  # Mobile device notify or other action
      data_template:
        message: "Your mug is at the desired {{ states('sensor.jesse_s_ember_mug') }}."

  - id: mug_battery_warning
    alias: Mug Battery Low
    trigger:
      - platform: numeric_state
        entity_id: sensor.jesse_s_ember_mug  # your mug entity
        value_template: "{{ state.attributes.battery_level }}"
        below: 20
        attribute: "battery_level"
        for:
          minutes: 10
    action:
      service: notify.mobile_app_jesse_s_pixel_4a  # Mobile device notify or other action
      data_template:
        message: "Your mug battery is low ({{ state_attr('sensor.jesse_s_ember_mug', 'battery_level') }}%)."

```