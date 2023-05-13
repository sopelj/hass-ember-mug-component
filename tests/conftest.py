"""Configure pytest."""
from unittest.mock import AsyncMock, Mock

from ember_mug import EmberMug
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
import pytest
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
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield


@pytest.fixture(autouse=True)
def mock_bluetooth(enable_bluetooth):
    """Auto mock bluetooth."""


@pytest.fixture
def mock_mug():
    """Create a mocked Ember Mug instance."""
    mock_mug = EmberMug(TEST_BLE_DEVICE)
    mock_mug._client = AsyncMock()
    mock_mug.update_initial = AsyncMock(return_value=[])
    mock_mug.update_all = AsyncMock(return_value=[])
    mock_mug.update_queued_attributes = AsyncMock(return_value=[])
    yield mock_mug


async def setup_platform(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
    platforms: list[str] | str,
    config: MockConfigEntry | None = None,
) -> MockConfigEntry:
    """Load the Mug integration with the provided mug and config for specified platform(s)."""
    if not isinstance(platforms, list):
        platforms = [platforms]

    if config is None:
        config = MockConfigEntry(
            domain=DOMAIN,
            title=TEST_MUG_NAME,
            data=DEFAULT_CONFIG_DATA,
            options=None,
            unique_id=TEST_MAC_UNIQUE_ID,
        )

    hass.config.components.add(DOMAIN)

    mug_coordinator = MugDataUpdateCoordinator(
        hass,
        Mock(),
        mock_mug,
        config.unique_id,
        config.data.get(CONF_NAME, config.title),
    )
    mug_coordinator.update_interval = None
    await mug_coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[config.entry_id] = HassMugData(
        mock_mug,
        mug_coordinator,
    )

    assert await async_setup_component(hass, DOMAIN, {}) is True

    # Check mug tried to update
    mock_mug.update_initial.assert_called_once()
    mock_mug.update_all.assert_called_once()

    for platform in platforms:
        assert (
            await hass.config_entries.async_forward_entry_setup(config, platform)
        ) is True

    # and make sure it completes before going further
    await hass.async_block_till_done()
    return config
