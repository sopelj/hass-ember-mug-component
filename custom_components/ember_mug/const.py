"""
Constants used for mug.

Most of these are UUIDs.
Since these are not public some were found on this repo https://github.com/orlopau/ember-mug/ (Thank you!)
Some found from testing and from the App.
"""
from typing import Final

DOMAIN = "ember_mug"
MANUFACTURER = "Ember"

ICON_DEFAULT = "mdi:coffee"
ICON_EMPTY = "mdi:coffee-off"

MUG_DEVICE_CLASS: Final[str] = "mug"

ATTR_RGB_COLOR = "rgb_color"
SERVICE_SET_LED_COLOUR = "set_led_colour"

ATTR_TARGET_TEMP = "target_temp"
SERVICE_SET_TARGET_TEMP = "set_target_temp"

SERVICE_SET_MUG_NAME = "set_mug_name"

ATTR_BATTERY_VOLTAGE = "battery_voltage"

# Constants for liquid state codes
LIQUID_STATE_UNKNOWN = 0
LIQUID_STATE_EMPTY = 1
LIQUID_STATE_FILLING = 2
LIQUID_STATE_COLD_NO_TEMP_CONTROL = 3
LIQUID_STATE_COOLING = 4
LIQUID_STATE_HEATING = 5
LIQUID_STATE_TARGET_TEMPERATURE = 6
LIQUID_STATE_WARM_NO_TEMP_CONTROL = 7

# Labels so liquid states
LIQUID_STATE_LABELS = {
    LIQUID_STATE_UNKNOWN: "Unknown",
    LIQUID_STATE_EMPTY: "Empty",
    LIQUID_STATE_FILLING: "Filling",
    LIQUID_STATE_COLD_NO_TEMP_CONTROL: "Cold (No control)",
    LIQUID_STATE_COOLING: "Cooling",
    LIQUID_STATE_HEATING: "Heating",
    LIQUID_STATE_TARGET_TEMPERATURE: "Perfect",
    LIQUID_STATE_WARM_NO_TEMP_CONTROL: "Warm (No control)",
}

LIQUID_STATE_TEMP_ICONS = {
    LIQUID_STATE_UNKNOWN: "thermometer-off",
    LIQUID_STATE_COLD_NO_TEMP_CONTROL: "thermometer-low",
    LIQUID_STATE_COOLING: "thermometer-chevron-down",
    LIQUID_STATE_HEATING: "thermometer-chevron-up",
    LIQUID_STATE_WARM_NO_TEMP_CONTROL: "thermometer-high",
}

# Validation
MUG_NAME_REGEX = r"[A-Za-z0-9,.\[\]#()!\"\';:|\-_+<>%= ]{1,16}"
MAC_ADDRESS_REGEX = r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$"
