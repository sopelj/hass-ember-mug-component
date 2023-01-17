"""Constants used for mug."""
from typing import Final

from ember_mug.consts import (
    LIQUID_STATE_COLD_NO_TEMP_CONTROL,
    LIQUID_STATE_COOLING,
    LIQUID_STATE_EMPTY,
    LIQUID_STATE_FILLING,
    LIQUID_STATE_HEATING,
    LIQUID_STATE_TARGET_TEMPERATURE,
    LIQUID_STATE_UNKNOWN,
    LIQUID_STATE_WARM_NO_TEMP_CONTROL,
)
from homeassistant.backports.enum import StrEnum

DOMAIN: Final[str] = "ember_mug"
MANUFACTURER: Final[str] = "Ember"

ICON_DEFAULT = "mdi:coffee"
ICON_EMPTY = "mdi:coffee-off"

ATTR_BATTERY_VOLTAGE = "battery_voltage"


class LiquidState(StrEnum):
    """Options for liquid state."""

    UNKNOWN = "unknown"
    EMPTY = "empty"
    FILLING = "filling"
    COLD_NO_CONTROL = "cold_no_control"
    COOLING = "cooling"
    HEATING = "heating"
    PERFECT = "perfect"
    WARM_NO_CONTROL = "warm_no_control"


LIQUID_STATE_OPTIONS = [ls for ls in LiquidState]
LIQUID_STATE_TEMP_ICONS = {
    LIQUID_STATE_UNKNOWN: "thermometer-off",
    LIQUID_STATE_COLD_NO_TEMP_CONTROL: "thermometer-low",
    LIQUID_STATE_COOLING: "thermometer-chevron-down",
    LIQUID_STATE_HEATING: "thermometer-chevron-up",
    LIQUID_STATE_WARM_NO_TEMP_CONTROL: "thermometer-high",
}

LIQUID_STATE_MAPPING = {
    LIQUID_STATE_UNKNOWN: LiquidState.UNKNOWN,
    LIQUID_STATE_EMPTY: LiquidState.EMPTY,
    LIQUID_STATE_FILLING: LiquidState.FILLING,
    LIQUID_STATE_COLD_NO_TEMP_CONTROL: LiquidState.COLD_NO_CONTROL,
    LIQUID_STATE_COOLING: LiquidState.COOLING,
    LIQUID_STATE_HEATING: LiquidState.HEATING,
    LIQUID_STATE_TARGET_TEMPERATURE: LiquidState.PERFECT,
    LIQUID_STATE_WARM_NO_TEMP_CONTROL: LiquidState.WARM_NO_CONTROL,
}

# Validation
MUG_NAME_REGEX = r"[A-Za-z0-9,.\[\]#()!\"\';:|\-_+<>%= ]{1,16}"
