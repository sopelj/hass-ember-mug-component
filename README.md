# Ember Mug Integration for Home Assistant

Custom integration for the Ember Mug in Home Assistant.
I only have the Ember Mug 2, but in theory it should be the same with other Ember Mugs.

This is still a work in progress, but seems to be working for reading information at least.
Although, I'm not sure what impact it has on battery.

The protocol is not public, so there is quite a bit of guesswork involved.
[@orlopau](https://github.com/orlopau) has documented the most important [UUIDs here](https://github.com/orlopau/ember-mug)

## Installation

Add to HACS as custom repository:

<https://github.com/sopelj/hass-ember-mug-component>

And then add to your configuration.yaml and add sensors for your mug(s):

```yaml
sensors:
  - platform: ember_mug
    mac: C9:0F:59:D6:33:F9
    name: "Jesse's Ember Mug"  # Optional Name
    temperature_unit: "C"  # Optional: Default [C]
```

For some reason, when Home Assistant boots up it will only pair with the mug if it is in pairing mode.
So, for now at least, when Home Assistant restarts you need to put your mug into pairing mode for it to be detected again. (Hold down 5 seconds until light flashes blue)