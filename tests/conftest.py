"""Configure pytest."""
from unittest.mock import AsyncMock, Mock

import pytest
from ember_mug import EmberMug
from ember_mug.data import ModelInfo
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ember_mug import DOMAIN, HassMugData, MugDataUpdateCoordinator
from tests import (
    DEFAULT_CONFIG_DATA,
    TEST_BLE_DEVICE,
    TEST_MAC_UNIQUE_ID,
    TEST_MUG_NAME,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def _auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    return


@pytest.fixture(autouse=True)
def _mock_bluetooth(enable_bluetooth):
    """Auto mock bluetooth."""


@pytest.fixture(autouse=True)
def _mock_dependencies(hass):
    """Mock dependencies loaded."""
    for component in ("http", "usb", "websocket_api", "bluetooth"):
        hass.config.components.add(component)


@pytest.fixture()
def mock_mug():
    """Create a mocked Ember Mug instance."""
    mock_mug = EmberMug(TEST_BLE_DEVICE, ModelInfo())
    mock_mug._client = AsyncMock()
    mock_mug._ensure_connection = AsyncMock()
    mock_mug.update_initial = AsyncMock(return_value=[])
    mock_mug.update_all = AsyncMock(return_value=[])
    mock_mug.update_queued_attributes = AsyncMock(return_value=[])
    return mock_mug


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
            unique_id=TEST_MAC_UNIQUE_ID,
        )

    config_entry.add_to_hass(hass)

    mug_coordinator = MugDataUpdateCoordinator(
        hass,
        Mock(),
        mock_mug,
        config_entry.unique_id,
        config_entry.data.get(CONF_NAME, config_entry.title),
    )
    mug_coordinator.update_interval = None
    await mug_coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = HassMugData(
        mock_mug,
        mug_coordinator,
    )

    assert await async_setup_component(hass, DOMAIN, {}) is True

    # Check mug tried to update
    mock_mug.update_initial.assert_called_once()
    mock_mug.update_all.assert_called_once()

    await hass.config_entries.async_forward_entry_setups(config_entry, platforms)

    # and make sure it completes before going further
    await hass.async_block_till_done()
    return config_entry
