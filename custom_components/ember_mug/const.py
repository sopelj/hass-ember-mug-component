DOMAIN = "ember_mug"

# https://github.com/orlopau/ember-mug/blob/master/docs/target-temp.md
TARGET_TEMP_UUID = "fc540003-236c-4c94-8fa9-944a3e5353fa"   # Target Temp (READ/WRITE)

# https://github.com/orlopau/ember-mug/blob/master/docs/mug-color.md
LED_COLOUR_UUID = "fc540014-236c-4c94-8fa9-944a3e5353fa"  # LED Colour (READ/WRITE)

# https://github.com/orlopau/ember-mug/blob/master/docs/current-temp.md
CURRENT_TEMP_UUID = "fc540002-236c-4c94-8fa9-944a3e5353fa"  # Current Temp (READ)

# https://github.com/orlopau/ember-mug/blob/master/docs/battery.md
BATTERY_UUID = "fc540007-236c-4c94-8fa9-944a3e5353fa"  # Current Battery (READ)

# https://github.com/orlopau/ember-mug/blob/master/docs/mug-state.md
STATE_UUID = "fc540012-236c-4c94-8fa9-944a3e5353fa"  # Get current State (READ/NOTIFICATION)

UNKNOWN_NOTIFY_UUID = "fc540013-236c-4c94-8fa9-944a3e5353fa"

ICON_DEFAULT = 'mdi:coffee'
ICON_UNAVAILABLE = 'mdi:coffee-off'


# https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/
# https://github.com/karepiu/custom_components/blob/master/lasko_bt_fan_w9560/fan.py
# https://github.com/pledi/EmberControl/blob/d19b7867ae5572a7da0e2ca9e68866fd28c613ed/main.py#L95


"""
[Service] fc543622-236c-4c94-8fa9-944a3e5353fa: Unknown
        [Characteristic] fc540013-236c-4c94-8fa9-944a3e5353fa: (notify) | Name: Unknown, Value: None 
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 51) | Value: b'\x00\x00' 
        [Characteristic] fc540014-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'\xff\xff\xff\xff'   # Colour
        [Characteristic] fc540012-236c-4c94-8fa9-944a3e5353fa: (notify) | Name: Unknown, Value: None     # State
                [Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 46) | Value: b'\x00\x00' 
        [Characteristic] fc540011-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'' 
                [Descriptor] 00002908-0000-1000-8000-00805f9b34fb: (Handle: 43) | Value: b' \x80\xf5u\x08\x00\xff\xff\x14\x00\xff\xff\x96@\xfe\xdf\x7f\xff\x14h' 
        [Characteristic] fc540010-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'\x00' 
        [Characteristic] fc54000f-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' 
        [Characteristic] fc54000e-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b'\xf6\x05\xc6]\xab\x86\x10b\x86\xa4,\x06\x94\x8fN\x18]\x95\xd5\xdb' 
        [Characteristic] fc54000d-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b'\xc9\x0fY\xd63\xf9-BBG04811704' 
        [Characteristic] fc54000c-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b't\x01\n\x00' 
        [Characteristic] fc54000a-236c-4c94-8fa9-944a3e5353fa: (write) | Name: Unknown, Value: None 
        [Characteristic] fc540008-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b'\x01' 
        [Characteristic] fc540007-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b'@\x00\xd8\x0e\x00'    # battery
        [Characteristic] fc540006-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'\x00\x00\x00\x00\x00' 
        [Characteristic] fc540005-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b'\x00' 
        [Characteristic] fc540004-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'\x01' 
        [Characteristic] fc540003-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'Z\x16'  # Target Temp
        [Characteristic] fc540002-236c-4c94-8fa9-944a3e5353fa: (read) | Name: Unknown, Value: b'\xc4\t'   # Current Temp
        [Characteristic] fc540001-236c-4c94-8fa9-944a3e5353fa: (read,write) | Name: Unknown, Value: b'EMBER' 

"""