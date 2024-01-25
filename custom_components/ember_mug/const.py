"""Constants used for mug."""
from typing import Final

from ember_mug.consts import LiquidState
from homeassistant.backports.enum import StrEnum

DOMAIN: Final[str] = "ember_mug"
MANUFACTURER: Final[str] = "Ember"
SUGGESTED_AREA: Final[str] = "Kitchen"

ICON_DEFAULT = "mdi:coffee"
ICON_EMPTY = "mdi:coffee-outline"
ICON_UNAVAILABLE = "mdi:coffee-off-outline"

ATTR_BATTERY_VOLTAGE = "battery_voltage"
CONF_INCLUDE_EXTRA = "include_extra"
CONF_DEBUG = "debug"


class LiquidStateValue(StrEnum):
    """Options for liquid state."""

    UNKNOWN = "unknown"
    STANDBY = "standby"
    EMPTY = "empty"
    FILLING = "filling"
    COLD_NO_CONTROL = "cold_no_control"
    COOLING = "cooling"
    HEATING = "heating"
    PERFECT = "perfect"
    WARM_NO_CONTROL = "warm_no_control"


LIQUID_STATE_OPTIONS = list(LiquidStateValue)
LIQUID_STATE_TEMP_ICONS = {
    None: "thermometer-off",
    LiquidState.STANDBY: "thermometer-off",
    LiquidState.COLD_NO_TEMP_CONTROL: "thermometer-low",
    LiquidState.COOLING: "thermometer-chevron-down",
    LiquidState.HEATING: "thermometer-chevron-up",
    LiquidState.WARM_NO_TEMP_CONTROL: "thermometer-high",
}

LIQUID_STATE_MAPPING = {
    None: LiquidStateValue.UNKNOWN,
    LiquidState.EMPTY: LiquidStateValue.EMPTY,
    LiquidState.FILLING: LiquidStateValue.FILLING,
    LiquidState.COLD_NO_TEMP_CONTROL: LiquidStateValue.COLD_NO_CONTROL,
    LiquidState.COOLING: LiquidStateValue.COOLING,
    LiquidState.HEATING: LiquidStateValue.HEATING,
    LiquidState.TARGET_TEMPERATURE: LiquidStateValue.PERFECT,
    LiquidState.WARM_NO_TEMP_CONTROL: LiquidStateValue.WARM_NO_CONTROL,
}
