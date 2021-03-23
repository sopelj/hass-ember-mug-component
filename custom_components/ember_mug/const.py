"""
Constants used for mug.

Most of these are UUIDs.
The purpose of all the UUIDs is not yet known. Some is guessing and testings.
Starting point was from this repo: https://github.com/orlopau/ember-mug/ Thank you!
"""
from uuid import UUID

DOMAIN = "ember_mug"

ICON_DEFAULT = "mdi:coffee"
ICON_UNAVAILABLE = "mdi:coffee-off"

ATTR_RGB_COLOR = "rgb_color"
SERVICE_SET_LED_COLOUR = "set_led_colour"

ATTR_TARGET_TEMP = "target_temp"
SERVICE_SET_TARGET_TEMP = "set_target_temp"

ATTR_MUG_NAME = "mug_name"
SERVICE_SET_MUG_NAME = "set_mug_name"

# Name of mug in byte string (Read/Write)
UUID_MUG_NAME = UUID("FC540001-236C-4C94-8FA9-944A3E5353FA")

# intValue(18, 0) -> temp (Read)
UUID_DRINK_TEMPERATURE = UUID("FC540002-236C-4C94-8FA9-944A3E5353FA")

# intValue(18, 0) -> temp (Read/Write)
UUID_TARGET_TEMPERATURE = UUID("FC540003-236C-4C94-8FA9-944A3E5353FA")

# intValue(17, 0) == 0 -> Celsius (Read/Write)
UUID_TEMPERATURE_UNIT = UUID("FC540004-236C-4C94-8FA9-944A3E5353FA")

# intValue(17, 0) -> Level (Between 0 -> 30 ?) 30 100% ?
UUID_LIQUID_LEVEL = UUID("FC540005-236C-4C94-8FA9-944A3E5353FA")

# Battery Info (Read)
# intValue(17, 0) -> float %
# intValue(17, 1) -> int == 1 -> connected to charger
UUID_BATTERY = UUID("FC540007-236C-4C94-8FA9-944A3E5353FA")

# Integer representing what it is doing with the liquid (Read)
UUID_LIQUID_STATE = UUID("FC540008-236C-4C94-8FA9-944A3E5353FA")
LIQUID_STATES = {
    1: "Empty",
    2: "Filling",
    4: "Cooling",
    5: "Heating",
    6: "Perfect",
}

# [Unique ID]-[serial number] (Read)
# [:6] -> ID in base64-ish
# [7:] -> Serial number in byte string
UUID_MUG_ID = UUID("FC54000D-236C-4C94-8FA9-944A3E5353FA")

# DSK - Unique ID used for auth in app (Read)
UUID_DSK = UUID("FC54000E-236C-4C94-8FA9-944A3E5353FA")
# UDSK - Used for auth in app (Read/Write)
UUID_UDSK = UUID("FC54000F-236C-4C94-8FA9-944A3E5353FA")

# TO watch for changes from mug (Notify/Read)
UUID_PUSH_EVENT = UUID("FC540012-236C-4C94-8FA9-944A3E5353FA")

# To gather bytes from mug for stats (Notify)
UUID_STATISTICS = UUID("FC540013-236C-4C94-8FA9-944A3E5353FA")

# RGBA Coloud of LED (Read/Write)
UUID_LED = UUID("FC540014-236C-4C94-8FA9-944A3E5353FA")

# Date/Time (Read/Write)
UUID_TIME_DATE_AND_ZONE = UUID("FC540006-236C-4C94-8FA9-944A3E5353FA")

# Last location - (Write)
UUID_LAST_LOCATION = UUID("FC54000A-236C-4C94-8FA9-944A3E5353FA")

# Firmware info (Read)
# string getIntValue(18, 0) -> Firmware version
# string getIntValue(18, 2) -> Hardware
# string getIntValue(18, 4) -> Bootloader
UUID_OTA = UUID("FC54000C-236C-4C94-8FA9-944A3E5353FA")

# int/temp lock - Address (Read/Write)
UUID_CONTROL_REGISTER_ADDRESS = UUID("FC540010-236C-4C94-8FA9-944A3E5353FA")

# Battery charge info (Read/Write)
# id len(1) -> Voltage (bytes as ulong -> voltage in mv)
# if len(2) -> Charge Time
UUID_CONTROL_REGISTER_DATA = UUID("FC540011-236C-4C94-8FA9-944A3E5353FA")

# These UUIDs are currently unused. Not for this mug?
UUID_VOLUME = UUID("FC540009-236C-4C94-8FA9-944A3E5353FA")
UUID_ACCELERATION = UUID("FC54000B-236C-4C94-8FA9-944A3E5353FA")
