"""Constants used for mug."""
from typing import Final

from ember_mug.consts import (
    LIQUID_STATE_COLD_NO_TEMP_CONTROL,
    LIQUID_STATE_COOLING,
    LIQUID_STATE_HEATING,
    LIQUID_STATE_LABELS,
    LIQUID_STATE_UNKNOWN,
    LIQUID_STATE_WARM_NO_TEMP_CONTROL,
)

DOMAIN: Final[str] = "ember_mug"
MANUFACTURER: Final[str] = "Ember"

ICON_DEFAULT = "mdi:coffee"
ICON_EMPTY = "mdi:coffee-off"

ATTR_BATTERY_VOLTAGE = "battery_voltage"

LIQUID_STATE_TEMP_ICONS = {
    LIQUID_STATE_UNKNOWN: "thermometer-off",
    LIQUID_STATE_COLD_NO_TEMP_CONTROL: "thermometer-low",
    LIQUID_STATE_COOLING: "thermometer-chevron-down",
    LIQUID_STATE_HEATING: "thermometer-chevron-up",
    LIQUID_STATE_WARM_NO_TEMP_CONTROL: "thermometer-high",
}

LIQUID_STATE_DISPLAY_OPTIONS = list(LIQUID_STATE_LABELS.values())

# Validation
MUG_NAME_REGEX = r"[A-Za-z0-9,.\[\]#()!\"\';:|\-_+<>%= ]{1,16}"
MAC_ADDRESS_REGEX = r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$"
