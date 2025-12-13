"""Test Ember Mug Integration init."""

from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ember_mug import DOMAIN
from custom_components.ember_mug.const import CONF_DEBUG, CONFIG_VERSION
from tests import (
    CONFIG_DATA_V1,
    CONFIG_DATA_V2,
    DEFAULT_CONFIG_DATA,
    TEST_BLE_DEVICE,
    TEST_MAC_UNIQUE_ID,
    TEST_MUG_NAME,
)
from tests.conftest import inject_ble_device_discovery_info


@patch("custom_components.ember_mug.coordinator.try_initial_setup", AsyncMock())
@patch("custom_components.ember_mug.EmberMug._update_multiple", return_value=[])
async def test_init(
    mock_update_multiple: Mock,
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
    inject_ble_device_discovery_info(hass, TEST_BLE_DEVICE)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.data.get(DOMAIN)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.parametrize(
    ("start_version", "input_config", "expected_options"),
    [
        (1, CONFIG_DATA_V1, {CONF_DEBUG: False}),
        (2, CONFIG_DATA_V2, {CONF_DEBUG: True}),
    ],
)
@patch("custom_components.ember_mug.coordinator.try_initial_setup", AsyncMock())
@patch("custom_components.ember_mug.EmberMug._update_multiple", return_value=[])
async def test_init_migration_v1(
    mock_update_multiple: Mock,
    hass: HomeAssistant,
    start_version: int,
    input_config: dict[str, Any],
    expected_options: dict[str, bool],
):
    """Test upgrading from V1 config to V3."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_MUG_NAME,
        data=input_config,
        options=None,
        unique_id=TEST_MAC_UNIQUE_ID,
        version=start_version,
    )
    mock_config_entry.add_to_hass(hass)
    inject_ble_device_discovery_info(hass, TEST_BLE_DEVICE)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.version == CONFIG_VERSION
    assert mock_config_entry.data == DEFAULT_CONFIG_DATA
    assert mock_config_entry.options == expected_options
