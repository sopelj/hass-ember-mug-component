"""Temp utils to try and enable writing."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING

from bleak import BleakError
from ember_mug.consts import MugCharacteristic
from ember_mug.utils import encode_byte_string

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from bleak import BleakClient


async def try_initial_setup(client: BleakClient) -> None:
    """Try and initialize the device for usage."""
    _LOGGER.debug("Attempt to initialize device: %s", client.address)

    # Try pairing. Errors are raised in pairing impossible or if it's already paired.
    with contextlib.suppress(BleakError, EOFError):
        await client.pair()
        _LOGGER.debug("Paired to device: %s", client.address)

    # Try and make writable
    with contextlib.suppress(BleakError):
        udsk_data = await client.read_gatt_char(MugCharacteristic.UDSK)
        _LOGGER.debug("Device %s as UDSK %s", client.address, str(udsk_data))
        if udsk_data != bytearray([0] * 20):
            # Already set. Ignore
            return
        # Write random string for test
        await client.write_gatt_char(
            MugCharacteristic.UDSK,
            bytearray(encode_byte_string("sad")),
        )
        _LOGGER.debug("UDSK Written to %s", client.address)
