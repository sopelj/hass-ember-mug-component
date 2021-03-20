"""
Constants used for mug.

Most of these are UUIDs.
The purpose of all the UUIDs is not yet known. Some is guessing and testings.
Starting point was from this repo: https://github.com/orlopau/ember-mug/ Thank you!
"""
from uuid import UUID

DOMAIN = "ember_mug"

# https://github.com/orlopau/ember-mug/blob/master/docs/target-temp.md
TARGET_TEMP_UUID = UUID(
    "fc540003-236c-4c94-8fa9-944a3e5353fa"
)  # Target Temp (READ/WRITE)

# https://github.com/orlopau/ember-mug/blob/master/docs/mug-color.md
LED_COLOUR_UUID = UUID(
    "fc540014-236c-4c94-8fa9-944a3e5353fa"
)  # LED Colour (READ/WRITE)

# https://github.com/orlopau/ember-mug/blob/master/docs/current-temp.md
CURRENT_TEMP_UUID = UUID("fc540002-236c-4c94-8fa9-944a3e5353fa")  # Current Temp (READ)

# https://github.com/orlopau/ember-mug/blob/master/docs/battery.md
BATTERY_UUID = UUID("fc540007-236c-4c94-8fa9-944a3e5353fa")  # Current Battery (READ)

# https://github.com/orlopau/ember-mug/blob/master/docs/mug-state.md
STATE_UUID = UUID(
    "fc540012-236c-4c94-8fa9-944a3e5353fa"
)  # Get current State (READ/NOTIFICATION)
# + Descriptor 00002902-0000-1000-8000-00805f9b34fb

SERIAL_NUMBER_UUID = UUID("fc54000d-236c-4c94-8fa9-944a3e5353fa")

UNKNOWN_NOTIFY_UUID = UUID("fc540013-236c-4c94-8fa9-944a3e5353fa")
# Descriptor 00002902-0000-1000-8000-00805f9b34fb

UNKNOWN_READ_UUIDS = (
    "fc540010-236c-4c94-8fa9-944a3e5353fa",
    "fc54000f-236c-4c94-8fa9-944a3e5353fa",
    "fc54000e-236c-4c94-8fa9-944a3e5353fa",
    "fc54000c-236c-4c94-8fa9-944a3e5353fa",
    "fc540008-236c-4c94-8fa9-944a3e5353fa",
    "fc540006-236c-4c94-8fa9-944a3e5353fa",
    "fc540005-236c-4c94-8fa9-944a3e5353fa",
    "fc540004-236c-4c94-8fa9-944a3e5353fa",
)

ICON_DEFAULT = "mdi:coffee"
ICON_UNAVAILABLE = "mdi:coffee-off"
