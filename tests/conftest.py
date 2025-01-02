"""Configure pytest."""

from logging import Logger
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bleak import BLEDevice
from ember_mug import EmberMug
from ember_mug.data import ModelInfo
from homeassistant.components.bluetooth import (
    SOURCE_LOCAL,
    BluetoothServiceInfoBleak,
    async_get_advertisement_callback,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ember_mug import CONFIG_VERSION, DOMAIN, MugDataUpdateCoordinator
from tests import (
    DEFAULT_CONFIG_DATA,
    MUG_SERVICE_INFO,
    TEST_BLE_DEVICE,
    TEST_MAC_UNIQUE_ID,
    TEST_MUG_NAME,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def _auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""


@pytest.fixture(autouse=True)
def _mock_bluetooth(enable_bluetooth: None) -> None:
    """Auto mock bluetooth."""


@pytest.fixture
def mock_mug():
    """Create a mocked Ember Mug instance."""
    mock_mug = EmberMug(TEST_BLE_DEVICE, ModelInfo())
    mock_mug._client = AsyncMock()
    mock_mug._ensure_connection = AsyncMock()
    mock_mug.update_initial = AsyncMock(return_value=[])
    mock_mug.update_all = AsyncMock(return_value=[])
    mock_mug.update_queued_attributes = AsyncMock(return_value=[])
    return mock_mug


def inject_ble_device_discovery_info(hass: HomeAssistant, device: BLEDevice):
    """Inject the device advertisement for Home Assistant."""
    service_info = {**MUG_SERVICE_INFO.as_dict()}
    service_info |= {
        "name": device.name or device.address,
        "address": device.address,
        "device": device,
        "source": SOURCE_LOCAL,
    }
    async_get_advertisement_callback(hass)(BluetoothServiceInfoBleak(**service_info))


async def setup_platform(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
    platforms: list[str] | str,
    config_entry: MockConfigEntry | None = None,
) -> MockConfigEntry:
    """Load the Mug integration with the provided mug and config for specified platform(s)."""
    if not isinstance(platforms, list):
        platforms = [platforms]

    if config_entry is None:
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            title=TEST_MUG_NAME,
            data=DEFAULT_CONFIG_DATA,
            options=None,
            version=CONFIG_VERSION,
            unique_id=TEST_MAC_UNIQUE_ID,
        )

    await async_setup_component(hass, DOMAIN, {})

    config_entry.add_to_hass(hass)
    inject_ble_device_discovery_info(hass, mock_mug.device)

    def get_coordinator(
        h: HomeAssistant,
        _l: Logger,
        _m: EmberMug,
        base_unique_id: str,
        device_name: str,
    ) -> MugDataUpdateCoordinator:
        coordinator = MugDataUpdateCoordinator(h, Mock(), mock_mug, base_unique_id, device_name)
        coordinator.persistent_data = {}
        coordinator._store = AsyncMock(async_load=AsyncMock(return_value=coordinator.persistent_data))
        return coordinator

    with (
        patch("custom_components.ember_mug.MugDataUpdateCoordinator", get_coordinator),
        patch("custom_components.ember_mug.PLATFORMS", platforms),
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Check mug tried to update
    mock_mug.update_initial.assert_called_once()
    mock_mug.update_all.assert_called_once()

    return config_entry
