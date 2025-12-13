"""Temp utils to try and enable writing."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING

from bleak import BleakError

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from bleak import BleakClient
    from ember_mug import EmberMug


async def try_pair(client: BleakClient):
    """Try pairing. Errors are raised in pairing impossible or if it's already paired."""
    with contextlib.suppress(BleakError, EOFError):
        await client.pair()
        _LOGGER.debug("Paired to device: %s", client.address)


async def try_initial_setup(mug: EmberMug) -> None:
    """Try and initialize the device for usage."""
    # Try and make writable
    try:
        udsk = mug.data.udsk
        _LOGGER.debug("Device %s as UDSK %s", mug.device.address, str(udsk))
        if udsk is not None:
            # Already set. Ignore
            _LOGGER.debug("UDSK %s is not undefined. Already setup.é", udsk)
            return
        # Write random string for test
        await mug.set_udsk("test-udsk")
    except BleakError as e:
        _LOGGER.debug("Failed to initialize device: %s. Error: %s", mug.device.address, e, exc_info=True)
