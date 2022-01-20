"""
Constants used for mug.

Most of these are UUIDs.
Since these are not public some were found on this repo https://github.com/orlopau/ember-mug/ (Thank you!)
Some found from testing and from the App.
"""
from uuid import UUID

EMBER_BLUETOOTH_NAMES = ["Ember Ceramic Mug"]

DOMAIN = "ember_mug"

ICON_DEFAULT = "mdi:coffee"
ICON_EMPTY = "mdi:coffee-off"

ATTR_RGB_COLOR = "rgb_color"
SERVICE_SET_LED_COLOUR = "set_led_colour"

ATTR_TARGET_TEMP = "target_temp"
SERVICE_SET_TARGET_TEMP = "set_target_temp"

ATTR_MUG_NAME = "mug_name"
SERVICE_SET_MUG_NAME = "set_mug_name"

ATTR_BATTERY_VOLTAGE = "battery_voltage"

# Name of mug in byte string (Read/Write)
UUID_MUG_NAME = UUID("fc540001-236c-4c94-8fa9-944a3e5353fa")

# intValue(18, 0) -> temp (Read)
UUID_DRINK_TEMPERATURE = UUID("fc540002-236c-4c94-8fa9-944a3e5353fa")

# intValue(18, 0) -> temp (Read/Write)
UUID_TARGET_TEMPERATURE = UUID("fc540003-236c-4c94-8fa9-944a3e5353fa")

# intValue(17, 0) == 0 -> Celsius (Read/Write)
UUID_TEMPERATURE_UNIT = UUID("fc540004-236c-4c94-8fa9-944a3e5353fa")

# intValue(17, 0) -> Level (Between 0 -> 30 ?) 30 100% ?
UUID_LIQUID_LEVEL = UUID("fc540005-236c-4c94-8fa9-944a3e5353fa")

# Battery Info (Read)
# [0] -> float %
# [1] -> int == 1 -> connected to charger
UUID_BATTERY = UUID("fc540007-236c-4c94-8fa9-944a3e5353fa")

# Integer representing what it is doing with the liquid (Read)
UUID_LIQUID_STATE = UUID("fc540008-236c-4c94-8fa9-944a3e5353fa")

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

EMBER_SERVICE_UUID = UUID("fc543622-236c-4c94-8fa9-944a3e5353fa")

# [Unique ID]-[serial number] (Read)
# [:6] -> ID in base64-ish
# [7:] -> Serial number in byte string
UUID_MUG_ID = UUID("fc54000d-236c-4c94-8fa9-944a3e5353fa")

# DSK - Unique ID used for auth in app (Read)
UUID_DSK = UUID("fc54000e-236c-4c94-8fa9-944a3e5353fa")

# UDSK - Used for auth in app (Read/Write)
UUID_UDSK = UUID("fc54000f-236c-4c94-8fa9-944a3e5353fa")

# TO watch for changes from mug (Notify/Read)
UUID_PUSH_EVENT = UUID("fc540012-236c-4c94-8fa9-944a3e5353fa")

# Push event codes
PUSH_EVENT_ID_BATTERY_CHANGED = 1
PUSH_EVENT_ID_CHARGER_CONNECTED = 2
PUSH_EVENT_ID_CHARGER_DISCONNECTED = 3
PUSH_EVENT_ID_TARGET_TEMPERATURE_CHANGED = 4
PUSH_EVENT_ID_DRINK_TEMPERATURE_CHANGED = 5
PUSH_EVENT_ID_AUTH_INFO_NOT_FOUND = 6
PUSH_EVENT_ID_LIQUID_LEVEL_CHANGED = 7
PUSH_EVENT_ID_LIQUID_STATE_CHANGED = 8
PUSH_EVENT_ID_BATTERY_VOLTAGE_STATE_CHANGED = 9

PUSH_EVENT_BATTERY_IDS = [
    PUSH_EVENT_ID_BATTERY_CHANGED,
    PUSH_EVENT_ID_CHARGER_CONNECTED,
    PUSH_EVENT_ID_CHARGER_DISCONNECTED,
]

# To gather bytes from mug for stats (Notify)
UUID_STATISTICS = UUID("fc540013-236c-4c94-8fa9-944a3e5353fa")

# RGBA Colour of LED (Read/Write)
UUID_LED = UUID("fc540014-236c-4c94-8fa9-944a3e5353fa")

# Date/Time (Read/Write)
UUID_TIME_DATE_AND_ZONE = UUID("fc540006-236c-4c94-8fa9-944a3e5353fa")

# Last location - (Write)
UUID_LAST_LOCATION = UUID("fc54000a-236c-4c94-8fa9-944a3e5353fa")

# Firmware info (Read)
# string [:2] -> Firmware version
# string [2:4] -> Hardware
# string [4:] -> Bootloader
UUID_OTA = UUID("fc54000c-236c-4c94-8fa9-944a3e5353fa")

# int/temp lock - Address (Read/Write)
UUID_CONTROL_REGISTER_ADDRESS = UUID("fc540010-236c-4c94-8fa9-944a3e5353fa")

# Battery charge info (Read/Write)
UUID_CONTROL_REGISTER_DATA = UUID("fc540011-236c-4c94-8fa9-944a3e5353fa")

# These UUIDs are currently unused. Not for this mug?
UUID_VOLUME = UUID("fc540009-236c-4c94-8fa9-944a3e5353fa")
UUID_ACCELERATION = UUID("fc54000b-236c-4c94-8fa9-944a3e5353fa")

# Validation
MUG_NAME_REGEX = r"[A-Za-z0-9,.\[\]#()!\"\';:|\-_+<>%= ]{1,16}"
MAC_ADDRESS_REGEX = r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$"
