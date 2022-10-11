# [Ember Mug Integration for Home Assistant](https://github.com/sopelj/hass-ember-mug-component)

[![GitHub Release](https://img.shields.io/github/release/sopelj/hass-ember-mug-component.svg?style=for-the-badge)](https://github.com/sopelj/hass-ember-mug-component/releases)
[![License](https://img.shields.io/github/license/sopelj/hass-ember-mug-component.svg?style=for-the-badge)](LICENSE.md)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
![Project Maintenance](https://img.shields.io/maintenance/yes/2022.svg?style=for-the-badge)

![Device View](./examples/device_example.png)

Custom integration for the Ember Mug in Home Assistant.
I only have the Ember Mug 2, but in theory it should be the same with other Ember Mugs.
Please let me know if you have another one and are willing to help test it.

The protocol is not public, so there is quite a bit of guesswork involved. 
[@orlopau](https://github.com/orlopau) did a great job documenting some [UUIDs here](https://github.com/orlopau/ember-mug) And had to attempt to extract the rest of them. 
The rest I had to do some testing and reverse engineering.

I can't seem to get writing to attributes working yet, but reading the data works great.
It seems to be a problem with the BlueZ dbus backend. Because it worked with gatttool before.

The actual Mug logic has been moved to [an external library](https://github.com/sopelj/python-ember-mug) as per the guidelines in Home Assistant. 
So if you have issues with the mug's internals and not the integration with home assistant please [raise issues there](https://github.com/sopelj/python-ember-mug/issues) :)

### **Important!** Older versions only work on certain versions of Home Assistant. If you have 2022.8 or newer just install the latest.
- Version < 0.3 Only works before 2022.8
- Version 0.3.X Works on 2022.8.X as long as the Bluetooth Integration is disabled
- Version 0.4+ Works on 2022.9+ and uses the new Bluetooth integration for discovery and setup

**If you had a version installed before 0.4 and are upgrading, please remove your mug before upgrading and it should be auto-discovered** 

Home Assistant has a list of [officially supported adaptors](https://www.home-assistant.io/integrations/bluetooth/#known-working-adapters), 
if you have connection issues, please try one of them.

## Installation / Setup

### Add Repository

Add to HACS as custom repository:

<https://github.com/sopelj/hass-ember-mug-component>

Install the integration in HACS and restart Home Assistant.

**You do not need to add the integration in Home Assistant. Just installing it is enough for autodiscovery to work**

### Setup Bluetooth Integration

Ensure you have the [Home Assistant Bluetooth Integration](https://www.home-assistant.io/integrations/bluetooth/) enabled, and you have your Bluetooth dongle setup.

![https://my.home-assistant.io/badges/config_flow_start.svg](https://my.home-assistant.io/redirect/config_flow_start?domain=bluetooth)

### Preparing your Mug

The Ember Mug is very finicky. It will only maintain a connection with one device at a time. 
If you have previously paired it with another device (like your phone) you will need to forget it from that device and reset the mug to factory settings.

*Note*: This will mean you cannot use that device to connect to at the same time as Home Assistant, and it will default to initial temperature and colour settings.

To do so:
 1. Forget the Mug on any device you previously used
 2. Hold down button on the bottom of the mug until light goes blue, then yellow and then red 
 3. It should blink red twice and goes back to white (The default colour) 
 4. Then enter pairing mode again - Hold down the button until the light starts blinking blue
 5. Home Assistant should auto-detect the mug and prompt you to configure it. Just hit next.

*Note* If it fails to find your mug please try resetting and entering pairing mode again before trying again.

## Caveats / known issues:

- The services to change mug values fail with a bluetooth permission error, that I can't figure out yet. 
- If you have another device paired with it like your phone it will cause it to disconnect, so you need to remove it from that device.
- This maintains a connection to your mug which:
    - may affect battery
    - may interfere with other local bluetooth integrations as it can only maintain one connection at a time.
- Currently, it won't work with more than one mug

## Examples

### Automations:

If you want to have notifications similar to the app you can do something like:

*Note*: If you chose a different name for you mug the sensor names may be different.

```yaml
automation:
  - id: mug_filled
    alias: Mug Filled
    trigger:
      - platform: state
        entity_id: sensor.mug  # your mug entity
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
        entity_id: sensor.mug
        attribute: liquid_state
        from:
          - "Heating"
          - "Cooling"
        to: "Perfect"
    action:
      service: notify.mobile_app_jesse_s_pixel_4a  # Mobile device notify or other action
      data_template:
        message: "Your mug is at the desired {{ states('sensor.mug_current_temp') }}{{ state_attr('sensor.mug_current_temp', 'unit_of_measurement') }}."

  - id: mug_battery_warning
    alias: Mug Battery Low
    trigger:
      - platform: numeric_state
        entity_id: sensor.mug_battery
        below: 20
        for:
          minutes: 10
    action:
      service: notify.mobile_app_jesse_s_pixel_4a  # Mobile device notify or other action
      data_template:
        message: "Your mug battery is low ({{ states('sensor.mug_battery') }}%)."

```

### Lovelace

An example for what I use in my lovelace config. 
This uses a couple custom lovelace cards, you could do something similar with base widgets, but I've used these here 
([battery-state-card](https://github.com/maxwroc/battery-state-card), [lovelace-multiple-entity-row](https://github.com/benct/lovelace-multiple-entity-row) and [stack-in-card](https://github.com/custom-cards/stack-in-card))

![Lovelace Example](./examples/lovelace_example.png)

```yaml
type: custom:stack-in-card
cards:
  - type: entities
    icon: mdi:coffee
    title: Ember Mug
    show_header_toggle: false
    entities:
      - entity: sensor.mug_current_temp
        type: custom:multiple-entity-row
        name: Temperature
        show_state: false
        entities:
          - entity: sensor.mug
            name: State
          - entity: sensor.mug_current_temp
            name: Current
          - entity: sensor.mug_target_temp
            name: Target
      - type: custom:template-entity-row
        entity: sensor.mug_liquid_level
        name: Liquid Level
        unit: '%'
      - type: custom:battery-state-entity
        name: Battery
        entity: sensor.mug_battery
        charging_state:
          attribute:
            name: battery_charging
            value: true
```
