# Changelog

## [0.7.0]

### Added
* Attempting to add support for Travel Mug

### Changes
* Entity ID prefix is changed for non "Mug" entities.
  * It is now: `ember_cup` for the Cup
  * And: `ember_travel_mug` for the Travel Mug.

## [0.6.1]

### Added
* Debug option in config (for development)
* Add support for Ember Cup
* Allow Travel Mug to be setup although, they are not supported yet.

## [0.6.0]

### Notes
* Requires Home Assistant 2023.4+

### Features
* Use new translations for entity names and state attributes

### Fixes
* Pairing with Bluetooth Proxies (just because of Home Assistant 2023.4)


## [0.5.2]

### Changes
* Request only connectable adapters

## [0.5.1]

### Notes
* Requires Home Assistant 2023.3+

### Fixed
* Compatibility with changes decimal precision option


## [0.5.0]

### Notes
* Requires Home Assistant 2023.2+
* Only supports Python 3.10+ (like 2023.2)

### Added
* Binary sensor for low battery warning
* Light Entity for Mug LED
* Text Entity for Mug Name
* Select Entity for Mug Temperature Unit
* Translations (en/fr) for entity states/attributes
* *Partial* support for Bluetooth Proxies

### Changed
* Target Temperature sensor was converted to editable Number Entity
* Entity IDs were renamed to follow standard format and facilitate multiple mugs `{domain}.ember_mug_{mac_address}_{name}`

### Removed
* Removed custom services. Replaced with built-in calls to new entities:
  * Mug Name: `text.set_value`
  * Temperature Unit: `select.select_option`
  * Target Temp: `number.set_value`
  * Mug LED: `light.turn_on` (Only changes RGB value. Turn Off and brightness do nothing.)

## [0.4.1]

### Added
* Add binary sensor for if the mug is on its base (Thanks @bwduncan!)

### Fixed
* Set unavailable on error (Thanks @winstona!)
* Don't try to pair on Bluetooth Proxies. (Doesn't fix proxies, but doesn't crash)

## [0.4.0]

### Added
* Support for the new Bluetooth Integration in Home Assistant 2022.8
* Automatic discovery of device

### Changed
* Changed to new Bluetooth Integration, so old device needs to be removed and re-added after update.

## [0.3.1]

### Fixed
*  Fix error decoding dsk for some people

## [0.3.0]

### Notes
* Only works on Home Assistant 2022.8 with Bluetooth Integration Disabled

### Fixed
* Fixes to make it run on Home Assistant 2022.8.X as long as the Bluetooth Integration is disabled

## [0.2.3]

### Fixed
* Bump bleak version

## [0.2.2]

### Fixed
* Add stack trace for debugging and test a few fixes
* Try top improve logging and update manifest with issues link

## [0.2.1]

### Added
* Config Flow: The integration can (and should) now be set up via the UI using config flow.

### Fixed
* Add stack trace for debugging and test a few fixes
* Try top improve logging and update manifest with issues link

## [0.1.2]

### Changed
* Update bleak to 0.13.0
* Update readme slightly

## [0.1.1]

### Changed
* Upgrade Bleak to 0.12.1

## [0.1.0]

### Added
* Initial Release

### Changed
* feat: Update doc, version number and add a license on principle.
