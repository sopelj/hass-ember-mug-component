"""Test Ember Mug Integration init."""
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ember_mug import DOMAIN
from tests import (
    DEFAULT_CONFIG_DATA,
    TEST_BLE_DEVICE,
    TEST_MAC_UNIQUE_ID,
    TEST_MUG_NAME,
    V1_CONFIG_DATA,
)


@patch(
    "custom_components.ember_mug.bluetooth.async_ble_device_from_address",
    return_value=TEST_BLE_DEVICE,
)
@patch("custom_components.ember_mug.EmberMug._update_multiple", return_value=[])
@patch("custom_components.ember_mug.asyncio.Event.wait", new_callable=AsyncMock)
async def test_init(
    mock_setup: Mock,
    mock_update_multiple: Mock,
    mock_async_event_wait: AsyncMock,
    hass: HomeAssistant,
) -> None:
    """Test initializing integration."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_MUG_NAME,
        data=DEFAULT_CONFIG_DATA,
        options=None,
        unique_id=TEST_MAC_UNIQUE_ID,
        version=2,
    )
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.data.get(DOMAIN)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


@patch(
    "custom_components.ember_mug.bluetooth.async_ble_device_from_address",
    return_value=TEST_BLE_DEVICE,
)
@patch("custom_components.ember_mug.EmberMug._update_multiple", return_value=[])
@patch("custom_components.ember_mug.asyncio.Event", new=AsyncMock)
async def test_init_migration(
    mock_setup: Mock,
    mock_update_multiple: Mock,
    hass: HomeAssistant,
):
    """Test upgrading from V1 config to V2."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_MUG_NAME,
        data=V1_CONFIG_DATA,
        options=None,
        unique_id=TEST_MAC_UNIQUE_ID,
        version=1,
    )
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.version == 2
