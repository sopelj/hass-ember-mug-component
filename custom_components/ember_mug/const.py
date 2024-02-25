"""Constants used for mug."""
from enum import StrEnum
from typing import Final

from ember_mug.consts import LiquidState

DOMAIN: Final[str] = "ember_mug"
MANUFACTURER: Final[str] = "Ember"
SUGGESTED_AREA: Final[str] = "Kitchen"
STORAGE_VERSION = 1
CONFIG_VERSION = 3

ICON_DEFAULT = "mdi:coffee"
ICON_EMPTY = "mdi:coffee-outline"
ICON_UNAVAILABLE = "mdi:coffee-off-outline"

ATTR_BATTERY_VOLTAGE = "battery_voltage"
CONF_DEBUG = "debug"
CONF_PRESETS = "presets"
CONF_PRESETS_UNIT = "presets_unit"

MIN_TEMP_CELSIUS: Final[float] = 48.8
MAX_TEMP_CELSIUS: Final[float] = 63

DEFAULT_PRESETS = {
    "latte": 55,
    "cappuccino": 56,
    "coffee": 57,
    "black-tea": 58.5,
    "green-tea": 59,
}


class LiquidStateValue(StrEnum):
    """Options for liquid state."""

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
    LiquidState.EMPTY: LiquidStateValue.EMPTY,
    LiquidState.FILLING: LiquidStateValue.FILLING,
    LiquidState.COLD_NO_TEMP_CONTROL: LiquidStateValue.COLD_NO_CONTROL,
    LiquidState.COOLING: LiquidStateValue.COOLING,
    LiquidState.HEATING: LiquidStateValue.HEATING,
    LiquidState.STANDBY: LiquidStateValue.STANDBY,
    LiquidState.TARGET_TEMPERATURE: LiquidStateValue.PERFECT,
    LiquidState.WARM_NO_TEMP_CONTROL: LiquidStateValue.WARM_NO_CONTROL,
}
